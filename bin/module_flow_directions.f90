!****************************************************************************************************  
!   Module flow directions
!
!   Input:
!       - dem 2d array (zdem)
!       
!
!   Output:
!       - flow directions 2d array (mat)
!
!                               
!     COMPUTE INDEX I,J                  1 3---------6--------9
!                                          !         !        !
!     0 NO FLOW   1....9 FLOW              !         !        !
!     I0=(MAT-1)/3-1              J AXIS 0 2---------0--------8
!                                          !         !        !
!     J0 = MAT-5-3*I0                      !         !        !
!                                       -1 1---------4--------7
!                                         -1         0        1
!                                                  I AXIS  
!****************************************************************************************************  

!----------------------------------------------------------------------------------------------------
! Module flow directions
module flow_directions

    implicit none
	
contains
	
    !----------------------------------------------------------------------------------------------------
    ! Subroutine to find flow directions
    subroutine fdir(zdem, mat)
        
        !----------------------------------------------------------------------------------------------------
        ! Variable(s) declaration
	real(kind = 4), dimension(:,:), intent(in)    	:: zdem
	integer(kind = 4), dimension(:,:), intent(out)  :: mat(size(zdem,1), size(zdem,2))
        
        real(kind = 4), dimension(:,:)			:: zz(size(zdem,1), size(zdem,2))
        integer(kind = 4), dimension(:,:)               :: mattmp(size(zz,1), size(zz,2))
	
	integer(kind = 4)                               :: i, j, ii, jj
	integer(kind = 4)                               :: i1, i2, j1, j2
	integer(kind = 4)                               :: iNCols, iNRows, idim, jdim
	real(kind = 4)                                  :: dem_min, dnodata, zi, z, p, pen
	!----------------------------------------------------------------------------------------------------
        
        !----------------------------------------------------------------------------------------------------
	! Variable(s) initialization
	dnodata = -9999; dem_min = -9999
	mat = 0; zz = 0.0

	zz = zdem
        !----------------------------------------------------------------------------------------------------
        
        !----------------------------------------------------------------------------------------------------
	! Get 2d variable dimensions
	iNCols = ubound(zz, dim=2) - lbound(zz, dim=2) + 1
	iNRows = ubound(zz, dim=1) - lbound(zz, dim=1) + 1

	idim=inrows
	jdim=incols
        !----------------------------------------------------------------------------------------------------
        
        ! Debug dem
        write(*,*) 'scrivo matrice dem debug'
        call debug_2dVar(dble(zdem), inrows, incols, 1)
        
        !----------------------------------------------------------------------------------------------------
        ! Check dem lower value
        dem_min = minval(minval(zz,DIM = 1, MASK=zz.ne.dnodata), DIM=1)
        write(*,*)'Dem lower value: ',dem_min
        if (dem_min<0) then 
            dem_min = abs(dem_min)+0.1
            where (zz.ne.dnodata)
                zz = zz + dem_min
            endwhere
        endif
        !----------------------------------------------------------------------------------------------------
        
        !----------------------------------------------------------------------------------------------------
        ! Call subroutine lake to do dem correction(s)
        call lake(zz)
        !----------------------------------------------------------------------------------------------------
        
        !----------------------------------------------------------------------------------------------------
        ! Compute pointer(s)
        do 1 i=1,jdim
            i1=-1
            i2=1
            if(i.eq.1)i1=0
            if(i.eq.jdim)i2=0
        
            do 2 j=1,idim
                mat(j,i)=0

                if(zz(j,i).lt.0) go to 2
                j1=-1
                j2=1
                if(j.eq.1)j1=0
                if(j.eq.idim)j2=0
                z=zz(j,i)
                pen=-1.e20
                
                do 3 ii=i1,i2
                    do 3 jj=j1,j2
                        p=zz(j+jj,ii+i)-z
                        p=-p
                        
                        if(p.le.0) go to 3
                        if(ii*jj.eq.0)go to 4
                        if(zz(j+jj,ii+i).ge.zz(j+jj,i)) go to 3
                        if(zz(j+jj,ii+i).ge.zz(j,ii+i)) go to 3
                        
                        zi=.25*(z+zz(j+jj,ii+i)+zz(j+jj,i)+zz(j,ii+i))
                        p=(zi-z)*sqrt(2.)
                        p=-p
                        
4                       if(p.le.pen) go to 3

                        pen=p
                        mat(j,i) = 3*ii+jj+5
3               continue
2          continue
1       continue
        !----------------------------------------------------------------------------------------------------
        
        !----------------------------------------------------------------------------------------------------
        ! Check Zeros		 
        !do i=3,jdim-2
        !    do j=3,idim-2
        !        !Controlla la quota 
        !        if(mat(j,i).eq.0.and.zz(j,i).ne.dnodata)then
        !
        !        endif
        !    enddo
        !enddo
        !----------------------------------------------------------------------------------------------------
        
        !----------------------------------------------------------------------------------------------------
        ! Convert pointer value(s) to dll c format
        mattmp=mat
        where(mattmp.eq.3)
            mat=7
        endwhere
        where(mattmp.eq.6)
            mat=8
        endwhere
        where(mattmp.eq.8)
            mat=6
        endwhere
        where(mattmp.eq.7)
            mat=3
        endwhere
        where(mattmp.eq.4)
            mat=2
        endwhere
        where(mattmp.eq.2)
            mat=4
        endwhere
        where(mattmp.le.0)
            mat=int(dnodata)
        endwhere
        
        ! Debug pointer(s)
        write(*,*) 'scrivo matrice puntatori debug'
        call debug_2dVar(dble(mat), inrows, incols, 2)
        !----------------------------------------------------------------------------------------------------
        
    end subroutine fdir
    !----------------------------------------------------------------------------------------------------
	  
    !----------------------------------------------------------------------------------------------------
    ! Subroutine lake
    subroutine lake(zz)
        
        !----------------------------------------------------------------------------------------------------
        ! Variable(s) declaration
        real(kind = 4), dimension(:,:), intent(inout)   :: zz

        integer(kind = 4)                               :: i,j, ii, jj, iii, jjj
        integer(kind = 4)                               :: i1, i2, j1, j2, ix, jx, kkk, kk
        integer(kind = 4)                               :: iNCols, iNRows, idim, jdim

        real(kind = 4)                                  :: zmin, zx

        integer(kind = 4), dimension(:,:)               :: mm(size(zz,1), size(zz,2))
        !----------------------------------------------------------------------------------------------------
        
        !----------------------------------------------------------------------------------------------------
        ! Variable(s) initialization
        mm = 0
        !----------------------------------------------------------------------------------------------------
        
        !----------------------------------------------------------------------------------------------------
        ! Get 2d variable dimensions
        iNCols = ubound(zz, dim=2) - lbound(zz, dim=2) + 1
        iNRows = ubound(zz, dim=1) - lbound(zz, dim=1) + 1

        idim=inrows
        jdim=incols
        !----------------------------------------------------------------------------------------------------
        
        !----------------------------------------------------------------------------------------------------
        ! Code to correct altitude values
        ! 0 = correct point
        ! 1 = deep point --> increasing value using zmin

        i1=-1
        i2=1
        j1=-1
        j2=1
        ix=2
        jx=2
        kkk=0
1000    kk=0

        do 11 i=ix,jdim-1
            do 10 j=jx,idim-1
      
                if(zz(j,i).lt.0) go to 10
                zmin=1.e20
                zx=zz(j,i)

                do 2 iii=i1,i2
                    do 2 jjj=j1,j2
                        if(iii.eq.0.and.jjj.eq.0) go to 22
                            ii=iii+i
                            jj=jjj+j
                            if(zx.gt.zz(jj,ii)) go to 10
                            if(zmin.gt.zz(jj,ii)) zmin=zz(jj,ii)
22                      continue
2               continue

                if(zx.le.zmin) then !Versione vecchio
                    zz(j,i)=zmin+.01 !!!Controllo quanto corregge
                    mm(j,i)=1
                    kkk=kkk+1
                    kk=1
                    if (i.ne.2)ix=i-1
                    if (j.ne.2)jx=j-1
                    
                    if(kkk/1000*1000.eq.kkk) then
                        write(*,'(i6,2i4,f8.2)')kkk,i,j,zz(j,i)
                    end if
                    
                    go to 1000
                    
                end if
10          continue
            jx=2
11      continue

        if(kk.eq.1) go to 1000
        
        ! Exit from subroutine
        return
        !----------------------------------------------------------------------------------------------------
        
    end subroutine lake
    !----------------------------------------------------------------------------------------------------

end module flow_directions
!----------------------------------------------------------------------------------------------------
