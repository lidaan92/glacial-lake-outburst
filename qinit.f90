
subroutine qinit(meqn, mbc, mx, my, xlower, ylower, dx, dy, q, maux, aux)
    
    use geoclaw_module, only: sea_level
    
    implicit none
    
    ! Subroutine arguments
    integer, intent(in) :: meqn,mbc,mx,my,maux
    real(kind=8), intent(in) :: xlower,ylower,dx,dy
    real(kind=8), intent(inout) :: q(meqn,1-mbc:mx+mbc,1-mbc:my+mbc)
    real(kind=8), intent(inout) :: aux(maux,1-mbc:mx+mbc,1-mbc:my+mbc)
    
    type lake_region
        ! Lake shoreline elevation
        real(kind=8) :: lake_level        

        ! Region specification
        real(kind=8) :: lower(2)
        real(kind=8) :: upper(2)
    end type lake_region

    type(lake_region), allocatable :: lake_regions(:)

    ! Locals
    integer :: i, j, n
    integer :: num_regions
    real(kind=8) :: x, y

    ! Lake Regions - Data for setting lake_level
    num_regions = 1
    allocate(lake_regions(num_regions))
    lake_regions(1)%lake_level = 5000.d0
    lake_regions(1)%lower = [0.d0, 1.d0]
    lake_regions(1)%upper = [0.d0, 1.d0]
    
    ! Set everything to zero
    q = 0.d0

    ! Loop through locations and set anything below given 
    do n = 1, num_regions
        do j = 1, my
            y = ylower + (j - 0.5d0) * dy
            do i = 1, mx
                x = xlower + (i - 0.5d0) * dx
                if (lake_regions(n)%lower(0) <= x .and.          &
                    x <= lake_regions(n)%upper(0) .and.          &
                    lake_regions(n)%lower(1) <= y .and.          &
                    y <= lake_regions(n)%upper(1)) then

                    q(1, i, j) = max(0.d0, lake_regions(n)%lake_level       &
                                           - aux(1, i, j))
                end if
            end do
        end do
    end do

end subroutine qinit
