!****************************************************************************************************  
!   Module drainage area
!
!   Input:
!       - dem 2d array (zq)
!       - flow directions 2d array (mat)
!
!   Output:
!       - area 2d array (zz)
!
!****************************************************************************************************  

!----------------------------------------------------------------------------------------------------
! Module drainage area
module drainage_area
    
    implicit none
    
contains
    
    !----------------------------------------------------------------------------------------------------
    ! Subroutine to compute drained area cell(s)
    subroutine darea(zq, mat_in, zz)
        
        !----------------------------------------------------------------------------------------------------
        ! Variable(s) declaration
	real(kind = 4), dimension(:,:), intent(in)    	:: zq
        integer(kind = 4), dimension(:,:), intent(in)   :: mat_in
        
	integer(kind = 4), intent(out) 			:: zz(size(zq,1), size(zq,2))
	
        integer(kind = 4)       			:: mattmp(size(zq,1), size(zq,2))
        integer(kind = 4)       			:: mat(size(zq,1), size(zq,2))
        
	integer(kind = 4)                               :: incols, inrows, idim, jdim
        real(kind = 4)                                  :: dnodata
	!----------------------------------------------------------------------------------------------------
        
        !----------------------------------------------------------------------------------------------------
	! Variable(s) initialization
	dnodata = -9999; 
	zz = -9999
        
        mat = mat_in
        !----------------------------------------------------------------------------------------------------
        
        !----------------------------------------------------------------------------------------------------
	! Get 2d variable dimensions
	iNCols = ubound(zz, dim=2) - lbound(zz, dim=2) + 1
	iNRows = ubound(zz, dim=1) - lbound(zz, dim=1) + 1

	idim=inrows
	jdim=incols
        !----------------------------------------------------------------------------------------------------
        
        call debug_2dVar(dble(zq), inrows, incols, 3)
        call debug_2dVar(dble(mat), inrows, incols, 4)
        
        !----------------------------------------------------------------------------------------------------
        ! Check pointers format (from ESRI to fortran default format)
        IF((maxval(maxval(mat,DIM = 1),DIM = 1)).gt.10)THEN
            mattmp=mat

            WHERE(mattmp.eq.32)
                mat=7 !Ok
            ENDWHERE
            WHERE(mattmp.eq.64)
                mat=8 !Ok
            ENDWHERE
            WHERE(mattmp.eq.128)
                mat=9 !Ok
            ENDWHERE
            WHERE(mattmp.eq.1)
                mat=6 !Ok
            ENDWHERE
            WHERE(mattmp.eq.2)
                mat=3	!Ok
            ENDWHERE
            WHERE(mattmp.eq.4)
                mat=2	!Ok
            ENDWHERE
            WHERE(mattmp.eq.8)
                mat=1 !Ok
            ENDWHERE
            WHERE(mattmp.eq.16)
                mat=4
            ENDWHERE

        ENDIF

        ! Convert to fortran notation
        where(mat.le.0)
            mat=0
        endwhere
        mattmp=mat
        
        if(1.eq.1)then
            where(mattmp.eq.7)
                mat=3
            endwhere
            where(mattmp.eq.8)
                mat=6
            endwhere
            where(mattmp.eq.6)
                mat=8
            endwhere
            where(mattmp.eq.3)
                mat=7
            endwhere
            where(mattmp.eq.2)
                mat=4
            endwhere
            where(mattmp.eq.4)
                mat=2
            endwhere

        endif
        !----------------------------------------------------------------------------------------------------
        
        !----------------------------------------------------------------------------------------------------
        ! Call subroutine integrals 
        call integrals(mat, zz)

        where (zq.lt.-200)
            zz = dnodata
        endwhere
        
        call debug_2dVar(dble(zz), inrows, incols, 5)
        
        write(*,*)'Area Max (number of cells): ',maxval(maxval(zz,DIM = 1),DIM = 1)
        !write(*,*)'Approssimative Area Max (Km^2): ',maxval(maxval(zz,DIM = 1),DIM = 1)*(dcellsize*100)**2
        !----------------------------------------------------------------------------------------------------
        
    end subroutine darea
    !----------------------------------------------------------------------------------------------------
	
    !----------------------------------------------------------------------------------------------------
    ! Subroutine to compute integrals 2d array
    subroutine integrals(mat, zz)
          
        !----------------------------------------------------------------------------------------------------
        ! Variable(s) declaration
        integer(kind = 4), dimension(:,:), intent(in)   :: mat
        
	integer(kind = 4), dimension(:,:), intent(out)  :: zz(size(mat,1), size(mat,2))
	
        integer(kind = 4)       			:: ms(size(mat,1), size(mat,2))

        integer(kind = 4)                               :: incols, inrows, idim, jdim
        integer(kind = 4)                               :: kk, kkk, i, j, i0, j0
        !----------------------------------------------------------------------------------------------------
        
        !----------------------------------------------------------------------------------------------------
	! Variable(s) initialization
        zz = 1; ms = 1;
        !----------------------------------------------------------------------------------------------------
        
        !----------------------------------------------------------------------------------------------------
	! Get 2d variable dimensions
	iNCols = ubound(mat, dim=2) - lbound(mat, dim=2) + 1
	iNRows = ubound(mat, dim=1) - lbound(mat, dim=1) + 1

	idim=inrows
	jdim=incols
        !----------------------------------------------------------------------------------------------------
        
        !----------------------------------------------------------------------------------------------------
        ! Compute zz integrals array
        do 1001 i=1,idim
            do 1002 j=1,jdim
                zz(j,i)=1
                ms(j,i)=1
1002        continue
1001    continue

        kkk=0
1000    kk=0
        do 2 i=1,idim
            do 3 j=1,jdim
                if(ms(j,i).eq.0) go to 3
                    if(mat(j,i).eq.0) go to 3
                    i0 = (mat(j,i) - 1)/3 - 1
                    j0 = mat(j,i) - 5 - 3*i0
                    i0 = i0 + i
                    j0 = j0 + j
              !     write(*,*)j0,i0
                    ms(j0,i0) = ms(j0,i0)+ms(j,i)
                    zz(j0,i0) = zz(j0,i0)+ms(j,i)
                    ms(j,i) = 0
                    kkk = kkk + 1
                    kk=1
3           continue
2       continue

        if(kk.eq.1) go to 1000

        return
        !----------------------------------------------------------------------------------------------------
        
    end subroutine integrals
    !----------------------------------------------------------------------------------------------------

end module drainage_area
!----------------------------------------------------------------------------------------------------
