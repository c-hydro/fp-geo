!****************************************************************************************************  
!   Module channels network
!
!   Input:
!       - dem 2d array
!       - flow directions 2d array
!       - dem mean step
!       - As^k value
!   Output:
!       - channels network 2d array
!               0 --> hills
!               1 --> channels
!              -1 --> undefined (sea, lakes ...)
!       - partial distance 2d array
!
!****************************************************************************************************     

!----------------------------------------------------------------------------------------------------
! Module channels distinction
module channels_network
    
    implicit none
    
contains
    
    !----------------------------------------------------------------------------------------------------
    ! Subroutine to compute channels network
    subroutine cnet(dem, pun_in, area, const, step, choice, pdistance)
        
        !----------------------------------------------------------------------------------------------------
        ! Variable(s) declaration
        real(kind = 4), dimension(:,:), intent(in)    	:: dem
        integer(kind = 4), dimension(:,:), intent(in)   :: pun_in
        integer(kind = 4), dimension(:,:), intent(in) 	:: area
        integer(kind = 4), intent(in)                   :: const, step
        
        real(kind = 4), intent(out)     :: pdistance(size(dem,1), size(dem,2))
        !real(kind = 4), intent(out)     :: fslope(size(dem,1), size(dem,2))
        integer(kind = 4), intent(out)	:: choice(size(dem,1), size(dem,2))
        
        real(kind = 4)          :: fslope(size(dem,1), size(dem,2))
        integer(kind = 4)      	:: pun(size(dem,1), size(dem,2))
        integer(kind = 4)      	:: mattmp(size(dem,1), size(dem,2))
        integer(kind = 4)     	:: musk(size(dem,1), size(dem,2))
        
        integer(kind = 4)                               :: incols, inrows, idim, jdim
        integer(kind = 4)                               :: i, j 
        
        real(kind = 4)                                  :: dnodata
        !----------------------------------------------------------------------------------------------------
        
        !----------------------------------------------------------------------------------------------------
        ! Variable initialization
        dnodata = -9999;
        pun = -9999; mattmp = -9999; musk = -9999;
        
        pdistance = -9999;
        choice = -1;  
        fslope = -9999 
        
        pun = pun_in
        !----------------------------------------------------------------------------------------------------
        
        !----------------------------------------------------------------------------------------------------
      	! Get 2d variable dimensions
	incols = ubound(dem, dim=2) - lbound(dem, dim=2) + 1
	inrows = ubound(dem, dim=1) - lbound(dem, dim=1) + 1
        jdim=inrows
	idim=incols
        !----------------------------------------------------------------------------------------------------

        !----------------------------------------------------------------------------------------------------
        ! Info
        write(*,*) 'Rows: ', iNRows
	write(*,*) 'Cols: ', iNCols
        write(*,*) 'AS^k threshold: ',const
        !----------------------------------------------------------------------------------------------------

        !----------------------------------------------------------------------------------------------------
        ! Musk definition
        musk = dnodata
        WHERE(dem.gt.-100)
            musk=1
        ENDWHERE
        !----------------------------------------------------------------------------------------------------
        
        !----------------------------------------------------------------------------------------------------
        ! Check pointers format (from ESRI to fortran default format)
        IF((maxval(maxval(pun,DIM = 1),DIM = 1)).gt.10)THEN
            mattmp=pun

            WHERE(mattmp.eq.32)
                    pun=7 !Ok
            ENDWHERE
            WHERE(mattmp.eq.64)
                    pun=8 !Ok
            ENDWHERE
            WHERE(mattmp.eq.128)
                    pun=9 !Ok
            ENDWHERE
            WHERE(mattmp.eq.1)
                    pun=6 !Ok
            ENDWHERE
            WHERE(mattmp.eq.2)
                    pun=3	!Ok
            ENDWHERE
            WHERE(mattmp.eq.4)
                    pun=2	!Ok
            ENDWHERE
            WHERE(mattmp.eq.8)
                    pun=1 !Ok
            ENDWHERE
            WHERE(mattmp.eq.16)
                    pun=4
            ENDWHERE

        ENDIF

        ! Convert to fortran notation
        where(pun.le.0)
            pun=0
        endwhere

        mattmp=pun

        if(1.eq.1)then
            where(mattmp.eq.7)
                pun=3
            endwhere
            where(mattmp.eq.8)
                pun=6
            endwhere
            where(mattmp.eq.6)
                pun=8
            endwhere
            where(mattmp.eq.3)
                pun=7
            endwhere
            where(mattmp.eq.2)
                pun=4
            endwhere
            where(mattmp.eq.4)
                pun=2
            endwhere
        endif
        !----------------------------------------------------------------------------------------------------
        
        !----------------------------------------------------------------------------------------------------
        ! Call subroutine scan
        call scan(1, idim, 1, jdim, 1, 1, & 
            dem, pun, area, &
            musk, &
            choice, pdistance, fslope, &
            step, const)
        
        !call debug_2dVar(dble(choice), jdim, idim, 1)
        !call debug_2dVar(dble(pdistance), jdim, idim, 2)
        !call debug_2dVar(dble(fslope), jdim, idim, 3)
            
        ! Filter slope using channels network array (choice)
        do j = 1,jdim
            do i = 1,idim
                if(choice(j,i).eq.0)then
                    fslope(j,i)=0
                endif
            enddo
        enddo
        
        !call debug_2dVar(dble(fslope), jdim, idim, 4)
        !----------------------------------------------------------------------------------------------------

    end subroutine cnet
    !----------------------------------------------------------------------------------------------------

    !----------------------------------------------------------------------------------------------------
    ! Subroutine scan to analyze domain array !scan(1,idim,1,jdim,1,1)
    subroutine scan(ist, ien, jst, jen, &
        istp, jstp, &
        dem, pun, area, &
        musk, &
        choice, pdistance, fslope, &
        step, const)
        
        !----------------------------------------------------------------------------------------------------
        ! Variable(s) declaration
        integer(kind = 4), dimension(:,:)   :: area
        real(kind = 4), dimension(:,:)      :: dem
        integer(kind = 4), dimension(:,:)   :: pun
        
        integer(kind = 4), dimension(:,:)   :: musk
        
        integer(kind = 4)                   :: const, step
        
        integer(kind = 4), dimension(:,:)   :: choice
        real(kind = 4), dimension(:,:)      :: pdistance
        real(kind = 4), dimension(:,:)      :: fslope
        
        integer(kind = 4)                   :: ist, ien, jst, jen
        integer(kind = 4)                   :: istp, jstp
        
        integer(kind = 4)                   :: i, ii, iii, j, jj, jjj
        integer(kind = 4)                   :: i0, j0, ifill
        
        integer(kind = 4)                   :: ihorc
        integer(kind = 4)                   :: pp
        
        logical                             :: noexit, nopit, new
        !----------------------------------------------------------------------------------------------------
                
        !----------------------------------------------------------------------------------------------------
        ! Cycle(s) over domain
        do j = jst, jen, jstp
            do i = ist ,ien ,istp
                
                !----------------------------------------------------------------------------------------------------
                ! Initialize counter(s) and boolean variable(s)
                noexit=.true.
                new=.false.
                ii=i
                jj=j
                ifill=0
                
                ! Compute choice and pdistance arrays
                do while (noexit)
                    
                    pp = pun(jj,ii)
                    
                    nopit = (pp.ne.0)

                    if (choice(jj,ii).eq.-1) new=.true.
                    if ((ifill.eq.1).and.(choice(jj,ii).eq.0)) new=.true.

                    if ((nopit).and.(new)) then
                        i0 = (pun(jj,ii)-1)/3-1
                        j0 = (pun(jj,ii)-5-3*i0)
                        iii = ii + i0
                        jjj = jj + j0

                        if (ifill.eq.1) then
                            choice(jj,ii)=1
                            pdistance(jj,ii) = distance(ii, jj, pun)
                            new=.false.
                        endif

                        if (ifill.eq.0) then
                            call comparison(ii, jj, ihorc, iii, jjj, &
                                dem, pun, area, musk, fslope, &
                                step, const)

                            choice(jj,ii) = ihorc
                            ifill = ihorc
                            pdistance(jj,ii) = distance(ii, jj, pun)
                            new=.false.
                        endif

                        ii=iii
                        jj=jjj
                        
                    else
                        noexit=.false.
                    endif
                    
                enddo
                !----------------------------------------------------------------------------------------------------
                
            enddo
        enddo
        !----------------------------------------------------------------------------------------------------
           
    end subroutine scan
    !----------------------------------------------------------------------------------------------------

    !----------------------------------------------------------------------------------------------------
    ! Subroutine comparison to find channels and hills
    subroutine comparison(id, jd, ihorc, iid, jjd, &
        dem, pun, area, musk, fslope, &
        step, const)

        !----------------------------------------------------------------------------------------------------
        ! Variable(s) declaration
        integer(kind = 4), dimension(:,:)   :: area
        real(kind = 4), dimension(:,:)      :: dem
        integer(kind = 4), dimension(:,:)   :: pun
        
        integer(kind = 4), dimension(:,:)   :: musk
        
        real(kind = 4), dimension(:,:)   :: fslope
        
        integer(kind = 4)                   :: const, step
        
        integer(kind = 4)                   :: id, jd, ihorc, iid, jjd
        real(kind = 4)                      :: rk
        real(kind = 4)                      :: ifT, ASK
        
        real(kind = 4)                      :: sm
        !----------------------------------------------------------------------------------------------------
        
        !----------------------------------------------------------------------------------------------------
        ! Variable(s) initialization 
        rk = 1.7  ! k exponent to compute AS^k to use for comparing with const threshold
        !----------------------------------------------------------------------------------------------------

        !----------------------------------------------------------------------------------------------------
        ! Call subroutine slope
        call slope(id, jd, iid, jjd, sm, step, dem, pun, musk, fslope)
        !----------------------------------------------------------------------------------------------------
        
        !----------------------------------------------------------------------------------------------------
        ! Threshold to test sm (temporary threshold evaluate to change in future)
        ifT = 1/10000 
        if(sm.lt.ifT) sm = ifT
        
        ! Evaluate AS^k threshold
        ASK = (area(jd,id)*step*step)*sm**rk
	
        if (ASK.le.const) then
            ihorc = 0
        else
            ihorc = 1
        endif
        !----------------------------------------------------------------------------------------------------

    end subroutine comparison 
    !----------------------------------------------------------------------------------------------------
    
    !----------------------------------------------------------------------------------------------------
    ! Subroutine slope to evaluate average slope
    subroutine slope(id, jd, iid, jjd, sm, step, dem, pun, musk, fslope)
        
        !----------------------------------------------------------------------------------------------------
        ! Variable(s) declaration
        real(kind = 4), dimension(:,:)      :: dem
        integer(kind = 4), dimension(:,:)   :: pun
        integer(kind = 4), dimension(:,:)   :: musk
        
        real(kind = 4), dimension(:,:)    :: fslope
        
        integer(kind = 4)                   :: id, jd, iid, jjd
        
        integer(kind = 4)                   :: step
        
        integer(kind = 4)                   :: icount
        real(kind = 4)                      :: sm, pmedia
        !----------------------------------------------------------------------------------------------------
        
        !----------------------------------------------------------------------------------------------------
        ! Compute average slope using pointers, dem and average dem step
        sm = (dem(jd,id)-dem(jjd,iid))/(distance(id, jd, pun)*step)
        icount=1

        if (pun(jd+1,id+1).eq.1) then
            sm = sm+(dem(jd+1,id+1)-dem(jd,id))/(1.41412356*step)
            icount = icount + 1
        endif

        if (pun(jd+1,id).eq.4) then
            sm = sm + (dem(jd+1,id)-dem(jd,id))/step
             icount = icount + 1
        endif

        if (pun(jd+1,id-1).eq.7) then
            sm = sm + (dem(jd+1,id-1)-dem(jd,id))/(1.41412356*step)
            icount = icount + 1
        endif

        if (pun(jd,id-1).eq.8) then
            sm = sm + (dem(jd,id-1)-dem(jd,id))/step
            icount = icount + 1
        endif

        if (pun(jd-1,id-1).eq.9) then
            sm = sm + (dem(jd-1,id-1)-dem(jd,id))/(1.41412356*step)
            icount = icount + 1
        endif

        if (pun(jd-1,id).eq.6) then
            sm = sm + (dem(jd-1,id)-dem(jd,id))/step
            icount = icount + 1
        endif

        if (pun(jd-1,id+1).eq.3) then
            sm = sm + (dem(jd-1,id+1)-dem(jd,id))/(1.41412356*step)
            icount = icount + 1
        endif

        if (pun(jd,id+1).eq.2) then
            sm = sm + (dem(jd,id+1)-dem(jd,id))/step
            icount = icount + 1
        endif
      
        if(sm.gt.4) then
            sm = 0
        end if

        sm = (sm/icount)
      
        if(musk(jd,id).eq.1) then
            pmedia = sm + pmedia
            fslope(jd,id) = sm
        end if
        !----------------------------------------------------------------------------------------------------

    end subroutine slope
    !----------------------------------------------------------------------------------------------------
      
    !----------------------------------------------------------------------------------------------------
    ! Function to compute distance between two indexes
    function distance (id, jd, pun) result(dist)
      
        !----------------------------------------------------------------------------------------------------
        ! Variable(s) declaration
        integer(kind = 4), dimension(:,:)   :: pun
      
        integer(kind = 4)                   :: id, jd
        integer(kind = 4)                   :: i0, j0
        real(kind = 4)                      :: dist
        !----------------------------------------------------------------------------------------------------
      
        !----------------------------------------------------------------------------------------------------
        ! Distance is a function of number of pixels following pointers array
        i0=(pun(jd,id)-1)/3-1
        j0=(pun(jd,id)-5-3*i0)
        if ((i0.eq.0).or.(j0.eq.0)) then
            dist=1
        else 
            dist=1.414
        endif
        !----------------------------------------------------------------------------------------------------
    
    end function distance
    !----------------------------------------------------------------------------------------------------

end module channels_network
!----------------------------------------------------------------------------------------------------
