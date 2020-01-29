!****************************************************************************************************  
!   Module coefficient resolution
!
!   Input:
!       - dem 2d array
!       - area 2d array
!       - channels network 2d array
!       - area cell 2d array
!       - resolution parameter value
!   Output:
!       - coefficient resolution 2d array
!
!****************************************************************************************************     

!----------------------------------------------------------------------------------------------------
! Module resolution coefficient
module coeff_resolution
    
    implicit none
    
contains
    
    !----------------------------------------------------------------------------------------------------
    ! Method to compute coefficient resolution
    subroutine cres(a2dDem, a2iArea, a2iChoice, a2dAreaCell, a2dCoeffResol, dRateResol)

        !----------------------------------------------------------------------------------------------------
        ! Variable(s) declaration
        real(kind = 4), dimension(:,:), intent(in)    	:: a2dDem
        real(kind = 4), dimension(:,:), intent(in)    	:: a2dAreaCell
        integer(kind = 4), dimension(:,:), intent(in)   :: a2iChoice
        integer(kind = 4), dimension(:,:), intent(in) 	:: a2iArea
        real(kind = 4), intent(in)                      :: dRateResol
        
        real(kind = 4), intent(out)         :: a2dCoeffResol(size(a2dDem,1), size(a2dDem,2))
        
        integer(kind = 4)                   :: a2iMask(size(a2dDem,1), size(a2dDem,2))
        real(kind = 4)                      :: a2dSecWidth(size(a2dDem,1), size(a2dDem,2))
        real(kind = 4)                      :: a2dArea(size(a2dDem,1), size(a2dDem,2))
        
        integer(kind = 4)                   :: incols, inrows, iRows,iCols
        
        real(kind = 4)                      :: dNCellMin, dACellMin, dCoffMean, dMaxW, dMinW
        !----------------------------------------------------------------------------------------------------

        !----------------------------------------------------------------------------------------------------
        ! Initialize variable(s)
        dNCellMin = -9999.0; dACellMin = -9999.0; dCoffMean= -9999.0; 
        dMaxW = -9999.0; dMinW = -9999.0;
        
        a2iMask = 0; a2dSecWidth = -9999; a2dCoeffResol = 1.0
        
        a2dArea = dble(a2iArea)
        !----------------------------------------------------------------------------------------------------
        
        !----------------------------------------------------------------------------------------------------
      	! Get 2d variable dimensions
	incols = ubound(a2dDem, dim=2) - lbound(a2dDem, dim=2) + 1
	inrows = ubound(a2dDem, dim=1) - lbound(a2dDem, dim=1) + 1
        iRows=inrows; iCols=incols
        !----------------------------------------------------------------------------------------------------
        
        !----------------------------------------------------------------------------------------------------
        ! Compute mask
        where(a2dDem.ge.0.0)
            a2iMask = 1
        endwhere
        !----------------------------------------------------------------------------------------------------
        
        !----------------------------------------------------------------------------------------------------
        ! Coeff to regulate subsurface and deep flow
        dNCellMin = MINVAL(MINVAL(a2dArea,dim=1,mask=a2iMask.gt.0.0.and.a2dArea.gt.0.0))
        dACellMin = MINVAL(MINVAL(a2dAreaCell,dim=1,mask=a2iMask.gt.0.0.and.a2dAreaCell.gt.0.0))
        write(*,*) 'Min CellNumber: ',dNCellMin, ' - Min CellArea: ',dACellMin       

        IF(dNCellMin.gt.1)THEN !Area matrix and not cells number matrix
                write(*,*)'Conversion from area to cell number'
                WHERE(a2dDem.gt.0.and.a2iChoice.gt.0)
                        a2dArea = a2dArea/a2dAreaCell*1000000 !Approximate formula
                ENDWHERE
        ENDIF
        !----------------------------------------------------------------------------------------------------

        !----------------------------------------------------------------------------------------------------
        ! Compute coeff map
        WHERE(a2dDem.gt.0.and.a2iChoice.ge.0)
                a2dCoeffResol = exp(-sqrt(a2dAreaCell)*0.0007)
        ENDWHERE    
        WHERE(a2dCoeffResol.lt.0)
                a2dCoeffResol=0.0
        ENDWHERE

        write(*,*),'Coeff Res Mean: ',a2dCoeffResol((iRows/2),(iCols/2))
        !----------------------------------------------------------------------------------------------------

    end subroutine cres
    !----------------------------------------------------------------------------------------------------

end module coeff_resolution
!----------------------------------------------------------------------------------------------------
