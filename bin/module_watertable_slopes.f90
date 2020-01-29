!****************************************************************************************************  
!   Module watertable slopes
!
!   Input:
!       - dem 2d array
!       - flow directions 2d array
!       - channels network 2d array
!       - cell area 2d array
!       - watertable parameter
!   Output:
!       - alpha 2d array
!       - beta 2d array
!
!****************************************************************************************************     

!----------------------------------------------------------------------------------------------------
! Module watertable slopes
module watertable_slopes
    
    implicit none

contains
    
    !----------------------------------------------------------------------------------------------------
    ! Subroutine to compute watertable slopes
    subroutine wslope(a2dDem_in, a2iPun, a2iChoice, a2dAreaCell, DD, a2dAlpha, a2dBeta)

        !----------------------------------------------------------------------------------------------------
        ! Variable(s) declaration
        real(kind = 8), dimension(:,:), intent(in)    	:: a2dDem_in, a2dAreaCell
        integer(kind = 4), dimension(:,:), intent(in)   :: a2iPun, a2iChoice

        real(kind = 8), intent(in)                      :: DD
        
        real(kind = 8), intent(out)                     :: a2dAlpha(size(a2dDem_in,1), size(a2dDem_in,2))
        real(kind = 8), intent(out)                     :: a2dBeta(size(a2dDem_in,1), size(a2dDem_in,2))
        
        real(kind = 8)          :: a2dDem(size(a2dDem_in,1), size(a2dDem_in,2))
        real(kind = 8)          :: pdistance(size(a2dDem_in,1), size(a2dDem_in,2)), LDD(size(a2dDem_in,1), size(a2dDem_in,2))
        real(kind = 8)          :: mask_perc_tot(size(a2dDem_in,1), size(a2dDem_in,2))
        real(kind = 8)          :: diff_DD(size(a2dDem_in,1), size(a2dDem_in,2))
        real(kind = 8)          :: pend(size(a2dDem_in,1), size(a2dDem_in,2))
        real(kind = 8)          :: pend2(size(a2dDem_in,1), size(a2dDem_in,2)), pend3(size(a2dDem_in,1), size(a2dDem_in,2))
        
        integer iRows, iCols
        integer i, ii, iii, j, jj, jjj, k, kk, kkk, ttt
        integer a, b, perc_tot
        integer ios

        real*4 pi, diff, fn, fMean, fNumPen
        real*4 dBmin, dBmax, dem_max
        real*4 dDistanceT, dDxM, dDyM
        !----------------------------------------------------------------------------------------------------
        
        !----------------------------------------------------------------------------------------------------
        ! Variable initialization
        LDD = 0.0
        pdistance = 0.0
        diff_DD = -9999.0

        mask_perc_tot = -9999.0
        pend = 0; pend2 = 0; pend3 = 0;

        a2dAlpha = -9999.0; a2dBeta = -9999.0
        
        a2dDem = a2dDem_in
        !----------------------------------------------------------------------------------------------------
        
        !----------------------------------------------------------------------------------------------------
      	! Get 2d variable dimensions
	iCols = ubound(a2dDem, dim=2) - lbound(a2dDem, dim=2) + 1
	iRows = ubound(a2dDem, dim=1) - lbound(a2dDem, dim=1) + 1
        !----------------------------------------------------------------------------------------------------
        
        !----------------------------------------------------------------------------------------------------
        ! Defining cell area mean value (x and y)
        dDxM = sqrt(sum(a2dAreaCell, mask=a2dAreaCell.gt.0.0) / count(a2dAreaCell.gt.0.0))
        dDyM = sqrt(sum(a2dAreaCell, mask=a2dAreaCell.gt.0.0) / count(a2dAreaCell.gt.0.0))
        !----------------------------------------------------------------------------------------------------

        !----------------------------------------------------------------------------------------------------
        ! Checking distance t
        dDistanceT=500
        IF(dDxM.ge.100.and.dDxM.lt.1000)THEN
             dDistanceT = 2000
        ENDIF
        IF(dDxM.ge.5000.and.dDxM.lt.20000)THEN
             dDistanceT = 30000
        ENDIF
        !----------------------------------------------------------------------------------------------------

        !----------------------------------------------------------------------------------------------------
        ! DEM Corrections
        where(a2dDem.le.0.and.a2dDem.gt.-1000)
                a2dDem = 0.2
        endwhere

        ! Lakes subroutine to correct depression area
        call lakes(iRows, iCols, a2dDem)
        !----------------------------------------------------------------------------------------------------

        !----------------------------------------------------------------------------------------------------
        ! Define alpha matrix angle
        perc_tot=0
        DO i = 1, iRows 
            DO j = 1, iCols 

                    a = i
                    b = j

                    IF(a2dDem(i,j).gt.0.0)THEN

                            perc_tot = perc_tot + 1
                            fNumPen = 0

                            DO WHILE((a2dDem(a,b).gt.0.0).and.diff_DD(a,b).eq.-9999)

                                    IF((a.gt.0.and.a.le.iRows).and.(b.gt.0.and.b.le.iCols))THEN

                                            iii = a + (INT((a2iPun(a,b)-1)/3)-1)
                                            jjj = b + a2iPun(a,b) - 5-3*(INT((a2iPun(a,b)-1)/3)-1)
                                            LDD(a,b) = SQRT(((a-iii)*dDyM)**2 + ((b-jjj)*dDxM)**2)

                                            IF(iii.lt.1.or.jjj.lt.1)THEN
                                                    EXIT
                                            ENDIF

                                            pdistance(a,b) = LDD(a,b)					
                                            diff_DD(a,b) = a2dDem(a,b)-a2dDem(iii,jjj)
                                            mask_perc_tot(a,b) = perc_tot

                                            !Pendenza media sui canali
                                            if(datan2(diff_DD(a,b),LDD(a,b)).gt.0.0)then
                                                    fNumPen=fNumPen+1
                                                    pend(a,b)=pend(a,b)+datan2(diff_DD(a,b),LDD(a,b))
                                            endif

                                            DO WHILE(a2dDem(a,b)-a2dDem(iii,jjj).le.DD .AND. &
                                                (iii.gt.0.and.iii.le.iRows).and.(jjj.gt.0.and.jjj.le.iCols) &
                                                .and.a2dDem(iii,jjj).gt.0.0.and.LDD(a,b).lt.dDistanceT)	

                                                    mask_perc_tot(a,b) = perc_tot
                                                    diff_DD(a,b) = a2dDem(a,b) - a2dDem(iii,jjj)
                                                    ii = iii + (INT((a2iPun(iii,jjj)-1)/3)-1)
                                                    jj = jjj + a2iPun(iii,jjj) - 5-3*(INT((a2iPun(iii,jjj)-1)/3)-1)	

                                                    IF(a2dDem(a,b)-a2dDem(ii,jj).le.DD &
                                                    .and.(ii.gt.0.and.ii.le.iRows).and.(jj.gt.0.and.jj.le.iCols))THEN	

                                                            LDD(a,b) = LDD(a,b) + SQRT(((ii-iii)*dDyM)**2+((jj-jjj)*dDxM)**2)

                                                            !Pendenza media sui canali
                                                            if(datan2(diff_DD(a,b),LDD(a,b)).gt.0.0)then
                                                                    if(a2iChoice(a,b).eq.1)then
                                                                            fNumPen = fNumPen + 1
                                                                            pend(a,b) = pend(a,b) + datan2(diff_DD(a,b),LDD(a,b))
                                                                    endif
                                                                    if(a2iChoice(a,b).eq.0.and.LDD(a,b).lt.500)then
                                                                            fNumPen = fNumPen + 1
                                                                            pend(a,b) = pend(a,b) + datan2(diff_DD(a,b),LDD(a,b))
                                                                    endif
                                                            endif

                                                    ENDIF

                                                    iii=ii
                                                    jjj=jj	

                                                    IF(diff_DD(iii,jjj).ne.-9999)THEN
                                                            DO WHILE(a2dDem(a,b)-a2dDem(iii,jjj).le.DD &
                                                                .AND.(iii.gt.0.and.iii.le.iRows).and. & 
                                                                (jjj.gt.0.and.jjj.le.iCols) &
                                                                .and.a2dDem(iii,jjj).gt.0.0 &
                                                                .and.LDD(a,b).lt.dDistanceT)	

                                                                    mask_perc_tot(a,b) = perc_tot					
                                                                    diff_DD(a,b) = a2dDem(a,b) - a2dDem(iii,jjj)
                                                                    ii = iii + (INT((a2iPun(iii,jjj)-1)/3)-1)
                                                                    jj = jjj + a2iPun(iii,jjj) - 5-3*(INT((a2iPun(iii,jjj)-1)/3)-1)	

                                                                    IF(a2dDem(a,b) - a2dDem(ii,jj).le.DD &
                                                                    .and.(ii.gt.0.and.ii.le.iRows) &
                                                                    .and.(jj.gt.0.and.jj.le.iCols))THEN	

                                                                            LDD(a,b) = LDD(a,b) + &
                                                                            SQRT(((ii-iii)*dDyM)**2+((jj-jjj)*dDxM)**2)

                                                                            !Pendenza media sui canali
                                                                            if(datan2(diff_DD(a,b),LDD(a,b)).gt.0.0)then
                                                                                    if(a2iChoice(a,b).eq.1)then
                                                                                            fNumPen = fNumPen + 1
                                                                                            pend(a,b) = pend(a,b) + &
                                                                                            datan2(diff_DD(a,b),LDD(a,b))
                                                                                    endif
                                                                                    if(a2iChoice(a,b).eq.0.and.LDD(a,b).lt.500)then
                                                                                            fNumPen = fNumPen + 1
                                                                                            pend(a,b) = pend(a,b) + &
                                                                                            datan2(diff_DD(a,b),LDD(a,b))
                                                                                    endif
                                                                            endif											
                                                                    ENDIF		
                                                                    iii=ii
                                                                    jjj=jj

                                                    ENDDO									
                                                ENDIF

                                            ENDDO					

                                            if(fNumPen.gt.0.0)then	
                                                    pend(a,b)=pend(a,b)/fNumPen
                                            endif

                                            a2dAlpha(a,b) = datan2(DD,LDD(a,b))  !Angolo in radianti

                                            if(diff_DD(a,b).lt.0.9.or.diff_DD(a,b).gt.500)then
                                                    diff_DD(a,b) = 0.9
                                            endif
                                            if(diff_DD(a,b).lt.1.and.LDD(a,b).lt.4*dDxM)then
                                                    LDD(a,b) = 4*dDxM
                                            endif

                                            a2dAlpha(a,b) = datan2(diff_DD(a,b),LDD(a,b))

                                            ii = a + (INT((a2iPun(a,b)-1)/3)-1)
                                            jj = b + a2iPun(a,b) - 5-3*(INT((a2iPun(a,b)-1)/3)-1)
                                            IF(a2dDem(ii,jj).gt.0.0)THEN
                                                    a=ii
                                                    b=jj
                                                    fNumPen=0
                                            ELSE
                                                    EXIT !esce ma conserva gli indici della fine percorso svolto
                                            ENDIF

                                    ENDIF

                            ENDDO !FINE DI UN PERCORSO COMPLETO SEGUENDO I PUNTATORI		

                            ii = a + (INT((a2iPun(a,b)-1)/3)-1)
                            jj = b + a2iPun(a,b) - 5-3*(INT((a2iPun(a,b)-1)/3)-1)

                ENDIF

                ENDDO
        ENDDO
        !----------------------------------------------------------------------------------------------------

        !----------------------------------------------------------------------------------------------------
        ! Define beta matrix angle
        a2dBeta = pend

        where(a2iChoice.lt.1)
                pend = 0
        endwhere

        pend2 = pend
        pend = 0

        ! Smoothing della pendenza sui canali
        DO i=1,iRows 
                DO j=1,iCols
                        if(a2iChoice(i,j).eq.1)then
                                fn=0
                                DO ii=i-1,i+1
                                        DO jj=j-1,j+1
                                                if(pend2(ii,jj).gt.0.0)then
                                                        fn=fn+1
                                                        pend(i,j)=pend(i,j)+pend2(ii,jj)
                                                endif
                                        ENDDO
                                ENDDO
                                if(fn.lt.1)fn=1
                                pend(i,j)=pend(i,j)/fn
                                if(LDD(i,j).le.4*dDxM.and.diff_DD(i,j).lt.2)then
                                        pend(i,j)=a2dAlpha(i,j)
                                endif
                                if(pend(i,j).gt.0.0)then
                                        a2dAlpha(i,j)=pend(i,j)
                                        a2dBeta(i,j)=pend(i,j)
                                endif
                        endif

                ENDDO
        ENDDO

        dBmin = minval(minval(pend,DIM = 1,MASK = pend.gt.0), DIM=1)

        where(a2dDem.gt.0.and.a2dBeta.eq.0)
                a2dBeta = a2dAlpha
        endwhere

        where(a2dDem.gt.0.and.a2dBeta.eq.0)
                a2dBeta = dBmin
        endwhere

        write(*,*) 'alpha max: ', maxval(maxval(a2dAlpha,DIM = 1),DIM = 1)
        write(*,*) 'alpha min: ', minval(minval(a2dAlpha,DIM = 1),DIM = 1)

        write(*,*) 'beta max: ', maxval(maxval(a2dBeta,DIM = 1),DIM = 1)
        write(*,*) 'beta min: ', minval(minval(a2dBeta,DIM = 1),DIM = 1)

        write(*,*) 'pend max: ', maxval(maxval(pend,DIM = 1),DIM = 1)
        write(*,*) 'pend min: ', minval(minval(pend,DIM = 1),DIM = 1)
        !----------------------------------------------------------------------------------------------------

    end subroutine wslope
    !----------------------------------------------------------------------------------------------------

    !----------------------------------------------------------------------------------------------------
    ! Subroutine lakes
    subroutine lakes(iRows, iCols, a2dDem)

        integer iRows, iCols
        integer i, ii, iii, j, jj, jjj, k, kk, kkk, ttt
        integer i1, i2, j1, j2, ix, jx

        real*8 zmin, zx

        real*8 a2dDem(iRows,iCols)

        i1 = -1
        i2 = 1
        j1 = -1
        j2 = 1
        ix = 2
        jx = 2
        kkk = 0
    500 kk = 0

        do 11 i = ix,iCols-1
            do 10 j = jx,iRows-1

            if(a2dDem(j,i).lt.0.0) go to 10

            zmin=1.e20
            zx=a2dDem(j,i)

            do 2 iii=i1,i2
                do 2 jjj=j1,j2

                if(iii.eq.0.and.jjj.eq.0) go to 22

                ii=iii+i
                jj=jjj+j

                if(zx.gt.a2dDem(jj,ii)) go to 10
                if(zmin.gt.a2dDem(jj,ii)) zmin=a2dDem(jj,ii)

    22          continue
    2           continue

                if(zx.le.zmin) then
                    a2dDem(j,i)=zmin+.4
                    kkk=kkk+1
                    kk=1
                    if (i.ne.2)ix=i-1
                    if (j.ne.2)jx=j-1

                    if(kkk/1000*1000.eq.kkk) then
                        write(*,'(i6,2i4,f8.2)')kkk,i,j,a2dDem(j,i)
                    end if

                    go to 500
                end if

    10          continue

            jx=2
    11      continue

            !write(*,*)'* ',kkk
            if(kk.eq.1) go to 500

    end subroutine lakes
    !----------------------------------------------------------------------------------------------------

end module watertable_slopes
!----------------------------------------------------------------------------------------------------
