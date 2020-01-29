!****************************************************************************************************  
!   Module corrivation time
!
!   Input:
!       - dem 2d array
!       - flow directions 2d array
!       - partial distance 2d array
!       - channels network 2d array
!       - jout point
!       - iout point
!
!   Output:
!       - ctime 2d array
!       - mask 2d array
!       - dem masked 2d array
!****************************************************************************************************  

!----------------------------------------------------------------------------------------------------
! Module corrivation time
module corrivation_time
    
    implicit none
    
contains

    !----------------------------------------------------------------------------------------------------
    ! Subroutine to compute section domain corrivation time 
    subroutine ctime(dem, ipun_in, pdistance, choice, uh, uc, jout_in, iout_in, ctimetot, mask, demmask)
        
        !----------------------------------------------------------------------------------------------------
        ! Variable(s) declaration
	real(kind = 4), dimension(:,:), intent(in)    	:: dem, pdistance, uh, uc
        integer(kind = 4), dimension(:,:), intent(in)   :: ipun_in, choice
        integer(kind = 4), intent(in)                   :: jout_in, iout_in
        
	real(kind = 4), intent(out) 			:: ctimetot(size(dem,1), size(dem,2))
        real(kind = 4), intent(out) 			:: demmask(size(dem,1), size(dem,2))
        integer(kind = 4), intent(out) 			:: mask(size(dem,1), size(dem,2))
	
        real(kind = 4)                                  :: demtmp(size(dem,1), size(dem,2))
        real(kind = 4)                                  :: cdistance(size(dem,1), size(dem,2))
        real(kind = 4)                                  :: rmask(size(dem,1), size(dem,2))
        real(kind = 4)                                  :: ctimetmp(size(dem,1), size(dem,2))
        integer(kind = 4)       			:: ipun(size(dem,1), size(dem,2))
        integer(kind = 4)       			:: mattmp(size(dem,1), size(dem,2))
        
        integer(kind = 4)                               :: iNRows, iNCols, idim, jdim
        integer(kind = 4)                               :: ioutfin, joutfin, jout, iout, cout
        
        real(kind = 4)                                  :: rindex, dnodata
        !----------------------------------------------------------------------------------------------------

        !----------------------------------------------------------------------------------------------------
	! Variable(s) initialization
	mattmp = -9999; cdistance = 0; rmask = -9999.0; ctimetot = -9999.0; 
        demtmp = -9999.0; demmask = -9999.0
        
        ctimetmp = 0; mask = 0;
         
        rindex = 1.0; dnodata = -9999.0

        demtmp = dem
        ipun = ipun_in
        
        jout = jout_in; iout = iout_in
        !----------------------------------------------------------------------------------------------------
        
        !----------------------------------------------------------------------------------------------------
	! Get 2d variable dimensions
	iNCols = ubound(dem, dim=2) - lbound(dem, dim=2) + 1
	iNRows = ubound(dem, dim=1) - lbound(dem, dim=1) + 1

        jdim = inrows
        idim = incols
        !----------------------------------------------------------------------------------------------------
        
        !----------------------------------------------------------------------------------------------------
        ! Define flow directions format
        IF((maxval(maxval(ipun,DIM = 1),DIM = 1)).gt.10)THEN
            mattmp=ipun

            WHERE(mattmp.eq.32)
                ipun=7 !Ok
            ENDWHERE
            WHERE(mattmp.eq.64)
                ipun=8 !Ok
            ENDWHERE
            WHERE(mattmp.eq.128)
                ipun=9 !Ok
            ENDWHERE
            WHERE(mattmp.eq.1)
                ipun=6 !Ok
            ENDWHERE
            WHERE(mattmp.eq.2)
                ipun=3	!Ok
            ENDWHERE
            WHERE(mattmp.eq.4)
                ipun=2	!Ok
            ENDWHERE
            WHERE(mattmp.eq.8)
                ipun=1 !Ok
            ENDWHERE
            WHERE(mattmp.eq.16)
                ipun=4
            ENDWHERE

        ENDIF
 
        ! Convert flow directions to fortran format
        where(ipun.le.0)
            ipun=0
        endwhere
        mattmp=ipun
        if(1.eq.1)then
            where(mattmp.eq.7)
                ipun=3
            endwhere
            where(mattmp.eq.8)
                ipun=6
            endwhere
            where(mattmp.eq.6)
                ipun=8
            endwhere
            where(mattmp.eq.3)
                ipun=7
            endwhere
            where(mattmp.eq.2)
                ipun=4
            endwhere
            where(mattmp.eq.4)
                ipun=2
            endwhere
        endif
        !----------------------------------------------------------------------------------------------------
        
        !----------------------------------------------------------------------------------------------------
        ! Get section i, j and info		 
        ioutfin = iout
        joutfin = jdim - jout + 1

        iout = ioutfin
        jout = joutfin
        
        cout = choice(jout,iout)
        
        ! Info outlet section value
        write(*,*)'Section jout_in, iout_in: ', jout_in, iout_in
        write(*,*)'Section jout_fortran, iout_fortran: ', jout, iout
        write(*,*)'Section Choice: ', cout
        !----------------------------------------------------------------------------------------------------
	
        !call debug_2dVar(dble(choice), jdim, idim, 1)
        !call debug_2dVar(dble(ipun), jdim, idim, 2)
        !call debug_2dVar(dble(pdistance), jdim, idim, 3)
        
        !----------------------------------------------------------------------------------------------------
        ! Call distance subroutine
        call dist(1, idim, 1, jdim, 1, 1, jout, iout, &
            ipun, pdistance, choice, cdistance, ctimetmp, uc, uh)
        ! Call mask preparation
        call mask_preparation(rindex, ctimetmp, rmask)
        !----------------------------------------------------------------------------------------------------
            
        !----------------------------------------------------------------------------------------------------
        ! Set nodata to ctime and dem array(s)
        where(ctimetmp.gt.0)
            ctimetot = ctimetmp
        endwhere

        where(rmask.ne.rindex)
            ctimetot = dnodata
        endwhere
        
        where(rmask.ne.rindex)
            demtmp = dnodata
        endwhere
        demmask = demtmp
        
        mask=int(rmask)
        !----------------------------------------------------------------------------------------------------
           	  
    end subroutine ctime
    !----------------------------------------------------------------------------------------------------

    !----------------------------------------------------------------------------------------------------
    ! Subroutine dist for computing cumulative distances and corrivation times
    !   - cdistance pdistance are musured in pixels
    !   - ctime is measured in pixel*s/m
    subroutine dist(ist, ien, jst, jen, istp, jstp, jout, iout, &
        ipun, pdistance, choice, cdistance, ctimetmp, uc, uh)

        !----------------------------------------------------------------------------------------------------
        ! Variable(s) declaration
        real(kind = 4), dimension(:,:)          :: cdistance, pdistance, uh, uc, ctimetmp
        integer(kind = 4), dimension(:,:)       :: ipun, choice

        logical                 :: exit, outlet, new, nopit

        integer(kind = 4)       :: i, j, ii, jj, iii, jjj, j0, i0
        integer(kind = 4)       :: ist, ien, jst, jen, istp, jstp
        integer(kind = 4)       :: iout, jout, idim, jdim, inrows, incols
        !----------------------------------------------------------------------------------------------------
        
        !----------------------------------------------------------------------------------------------------
        ! Get 2d variable dimensions
        iNCols = ubound(choice, dim=2) - lbound(choice, dim=2) + 1
	iNRows = ubound(choice, dim=1) - lbound(choice, dim=1) + 1

        jdim = inrows
        idim = incols
        !----------------------------------------------------------------------------------------------------

        !----------------------------------------------------------------------------------------------------
        ! Scan the basin matrix and calculating ctime and cdistance
        do j=jst,jen,jstp
            do i=ist,ien,istp
                
                !----------------------------------------------------------------------------------------------------
                ! Initilize variable(s)
                exit=.true.
                outlet=.false.
                new=.false.
                nopit=.false.
                ii=i
                jj=j
                if(cdistance(j,i).ne.0) exit=.false.
                !----------------------------------------------------------------------------------------------------
                
                !----------------------------------------------------------------------------------------------------
                ! Iterate until outlet point
                do while (exit)

                    !----------------------------------------------------------------------------------------------------
                    ! Point is outlet section
                    if ((jj.eq.jout).and.(ii.eq.iout)) then
                        outlet = .true.
                        cdistance(j,i) = cdistance(j,i) + pdistance(jj,ii)

                        if (choice(jj,ii).eq.0) then
                            !ctime(j,i)=ctime(j,i)+pdistance(jj,ii)/v0
                            ctimetmp(j,i) = ctimetmp(j,i) + pdistance(jj,ii)/uh(jj,ii)
                        else
                            !ctime(j,i)=ctime(j,i)+pdistance(jj,ii)/v1
                            ctimetmp(j,i) = ctimetmp(j,i) + pdistance(jj,ii)/uc(jj,ii)
                        endif

                        ! Fill time and distance paths to the outlet
                        call cascade(i, j, ii, jj, ipun, cdistance, pdistance, choice, ctimetmp, uh, uc)
                    endif
                    !----------------------------------------------------------------------------------------------------

                    !----------------------------------------------------------------------------------------------------
                    ! Point scanning initialization
                    if (ipun(jj,ii).ne.0) nopit=.true.
                    if (cdistance(jj,ii).eq.0) new=.true.
                    if (cdistance(jj,ii).eq.-9999.) exit=.false. 

                    if ((cdistance(jj,ii).ne.0).and.(cdistance(jj,ii) &
                        .ne.-9999).and.(.not.outlet)) then
                        cdistance(j,i) = cdistance(j,i) + cdistance(jj,ii)
                        ctimetmp(j,i) = ctimetmp(j,i) + ctimetmp(jj,ii)
                        ! Fill time and distance paths to an already scanned path
                        call cascade(i, j, ii, jj, ipun, cdistance, pdistance, choice, ctimetmp, uh, uc)
                        new=.false.
                    endif   
                    !----------------------------------------------------------------------------------------------------

                    !----------------------------------------------------------------------------------------------------
                    ! Point is not outlet section
                    if ((.not.outlet).and.(nopit).and.(new)) then            
                        i0 = (ipun(jj,ii)-1)/3 - 1
                        j0 = (ipun(jj,ii)-5) - 3*i0
                        iii = ii + i0
                        jjj = jj + j0
                        if (ipun(jjj,iii).eq.0) then
                            ! Fill time and distance paths with undefined values (out of matrix)
                            call undef(i, j, ii, jj, ipun, cdistance, ctimetmp)                     
                            exit=.false. 
                        endif
                        ! Compute first cumulative distance and corrivation time
                        if (exit) then
                            cdistance(j,i) = cdistance(j,i) + pdistance(jj,ii)
                            if (choice(jj,ii).eq.0) then
                               !ctime(j,i)=ctime(j,i)+pdistance(jj,ii)/v0
                               ctimetmp(j,i) = ctimetmp(j,i) + pdistance(jj,ii)/uh(jj,ii)
                            else
                               !ctime(j,i)=ctime(j,i)+pdistance(jj,ii)/v1
                               ctimetmp(j,i) = ctimetmp(j,i) + pdistance(jj,ii)/uc(jj,ii)
                            endif
                            ii=iii
                            jj=jjj
                        endif  

                        new=.false.
                        nopit=.false.

                    else

                        if (.not.exit) then
                            ! Fill time and distance paths with undefined values (undefined path)--
                           call undef(i, j, ii, jj, ipun, cdistance, ctimetmp)
                        endif
                        exit=.false.

                    endif
                    !----------------------------------------------------------------------------------------------------

                enddo
                !----------------------------------------------------------------------------------------------------

            enddo
        enddo
        !----------------------------------------------------------------------------------------------------

    end subroutine dist 
    !----------------------------------------------------------------------------------------------------

    !----------------------------------------------------------------------------------------------------
    ! Subroutine cascade
    subroutine cascade(id, jd, iid, jjd, &
        ipun, cdistance, pdistance, choice, ctimetmp, uh, uc)

        !----------------------------------------------------------------------------------------------------
        ! Variable(s) declaration
        real(kind = 4), dimension(:,:)          :: cdistance, pdistance, uh, uc, ctimetmp
        integer(kind = 4), dimension(:,:)       :: ipun, choice

        integer(kind = 4)       :: id, jd, iid, jjd
        integer(kind = 4)       :: ii, jj, iii, jjj, i0, j0

        logical exit
        !----------------------------------------------------------------------------------------------------

        !----------------------------------------------------------------------------------------------------
        exit=.true.      
        ii = id
        jj = jd
        do while (exit) 
            if ((jj.eq.jjd).and.(ii.eq.iid)) exit=.false.

            if (exit) then      
                i0 = (ipun(jj,ii)-1)/3-1
                j0 = (ipun(jj,ii)-5) - 3*i0
                iii = ii + i0
                jjj = jj + j0
                cdistance(jjj,iii) = cdistance(jj,ii) - pdistance(jj,ii)
                if (choice(jj,ii).eq.0) then
                   !ctime(jjj,iii)=ctime(jj,ii)-pdistance(jj,ii)/v0
                   ctimetmp(jjj,iii) = ctimetmp(jj,ii) - pdistance(jj,ii)/uh(jj,ii)
                else
                   !ctime(jjj,iii)=ctime(jj,ii)-pdistance(jj,ii)/v1
                   ctimetmp(jjj,iii) = ctimetmp(jj,ii) - pdistance(jj,ii)/uc(jj,ii)
                endif     

                ii = iii
                jj = jjj

            endif
        enddo

        return
        !----------------------------------------------------------------------------------------------------

    end subroutine cascade
    !----------------------------------------------------------------------------------------------------

    !----------------------------------------------------------------------------------------------------
    ! Subroutine undef
    subroutine undef(id, jd, iid, jjd, &
        ipun, cdistance, ctimetmp)

        !----------------------------------------------------------------------------------------------------
        ! Variable(s) declaration
        real(kind = 4), dimension(:,:)          :: cdistance, ctimetmp
        integer(kind = 4), dimension(:,:)       :: ipun

        integer(kind = 4)       :: id, jd, iid, jjd
        integer(kind = 4)       :: ii, jj, i0, j0

        logical exit
        !----------------------------------------------------------------------------------------------------

        !----------------------------------------------------------------------------------------------------
        ! Set undefined values to point not in domain
        exit=.true.
        ii=id
        jj=jd
        do while (exit)
            if((jj.eq.jjd).and.(ii.eq.iid)) exit=.false.
            cdistance(jj,ii) = -9999
            ctimetmp(jj,ii) = -9999
            i0 = (ipun(jj,ii)-1)/3-1
            j0 = (ipun(jj,ii)-5)-3*i0
            ii = ii + i0
            jj = jj + j0
        enddo
        return
        !----------------------------------------------------------------------------------------------------

    end subroutine undef
    !----------------------------------------------------------------------------------------------------

    !----------------------------------------------------------------------------------------------------
    ! Subroutine mask preparation
    subroutine mask_preparation(rindex, ctimetmp, rmask)

        !----------------------------------------------------------------------------------------------------
        ! Variable(s) declaration
        real(kind = 4), dimension(:,:)              :: rmask, ctimetmp

        integer(kind = 4)   :: i,j, idim, jdim, iNCols, iNRows
        real(kind = 4)      :: rindex
        !----------------------------------------------------------------------------------------------------
        
        !----------------------------------------------------------------------------------------------------
	! Get 2d variable dimensions
	iNCols = ubound(ctimetmp, dim=2) - lbound(ctimetmp, dim=2) + 1
	iNRows = ubound(ctimetmp, dim=1) - lbound(ctimetmp, dim=1) + 1

        jdim = inrows
        idim = incols
        !----------------------------------------------------------------------------------------------------
        
        !----------------------------------------------------------------------------------------------------
        ! Compute mask
        do i=1,idim
            do j=1,jdim
                if ((ctimetmp(j,i).ne.-9999).and.(ctimetmp(j,i).ne.0)) rmask(j,i)=rindex
            enddo
        enddo
        return
        !----------------------------------------------------------------------------------------------------

    end subroutine mask_preparation
    !----------------------------------------------------------------------------------------------------

end module corrivation_time
!----------------------------------------------------------------------------------------------------
