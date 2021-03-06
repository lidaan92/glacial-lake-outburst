
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

    type(lake_region), allocatable :: lake_regions(:), cutout_regions(:)

    ! Locals
    integer :: i, j, n, k, region
    integer :: num_regions
    real(kind=8) :: xm, x, xp, ym, y, yp, x_c, y_c

    ! Lake Regions - Data for setting lake_level
    num_regions = 1
    allocate(lake_regions(num_regions))

    lake_regions(1)%lake_level = 5000.d0
    lake_regions(1)%lower = [86.910814d0, 27.883193d0]
    lake_regions(1)%upper = [86.951576d0, 27.912485d0]

    ! Loop through locations and set anything below given 
    do j = 1, my
        ym = ylower + j * dy
        y = ylower + (j - 0.5d0) * dy
        yp = ylower + (j + 1.d0) * dy
        do i = 1, mx
            xm = xlower + i * dx
            x = xlower + (i - 0.5d0) * dx
            xp = xlower + (i + 1.d0) * dx

            do n = 1, num_regions
                if (lake_regions(n)%lower(1) <= xm .and.            &
                    xp <= lake_regions(n)%upper(1) .and.            &
                    lake_regions(n)%lower(2) <= ym .and.            &
                    yp <= lake_regions(n)%upper(2)) then

                    q(1, i, j) = max(0.d0, lake_regions(n)%lake_level &
                             - aux(1, i, j))

                end if
            end do
        end do
    end do

end subroutine qinit