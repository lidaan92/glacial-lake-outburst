
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
    integer :: i, j, n, k
    integer :: num_regions, num_cutouts
    real(kind=8) :: x, y, sigma, deta, A, x_c, y_c, total_mass
    logical :: cutout

    ! Lake Regions - Data for setting lake_level
    num_regions = 1
    allocate(lake_regions(num_regions))
    lake_regions(1)%lake_level = 5000.d0
    lake_regions(1)%lower = [491010.d0, 3086250.d0]
    lake_regions(1)%upper = [493710.d0, 3087250.d0]

    num_cutouts = 3
    allocate(cutout_regions(num_cutouts))
    cutout_regions(1)%lower = [491000.d0, 3086900.d0]
    cutout_regions(1)%upper = [491900.d0, 3087250.d0]

    cutout_regions(2)%lower = [491000.d0, 3086800.d0]
    cutout_regions(2)%upper = [491400.d0, 3087250.d0]
    
    cutout_regions(3)%lower = [491010.d0, 3086250.d0]
    cutout_regions(3)%upper = [493710.d0, 3087250.d0]

    A = 100.d0
    sigma = 100.d0
    x_c = 493000.d0
    y_c = 3086700.d0
    
    ! Set everything to zero
    q = 0.d0
    total_mass = 0.d0

    ! Loop through locations and set anything below given 
    do n = 1, num_regions
        do j = 1, my
            y = ylower + (j - 0.5d0) * dy
            do i = 1, mx
                x = xlower + (i - 0.5d0) * dx
                if (lake_regions(n)%lower(1) <= x .and.                     &
                    x <= lake_regions(n)%upper(1) .and.                     &
                    lake_regions(n)%lower(2) <= y .and.                     &
                    y <= lake_regions(n)%upper(2)) then

                    cutout = .false.
                    do k = 1, num_cutouts
                        if (cutout_regions(n)%lower(1) <= x .and.           &
                            x <= cutout_regions(n)%upper(1) .and.           &
                            cutout_regions(n)%lower(2) <= y .and.           &
                            y <= cutout_regions(n)%upper(2)) then

                            cutout = .true.
                        end if
                    end do
                    if (.not.cutout) then
                        q(1, i, j) = max(0.d0, lake_regions(n)%lake_level &
                                     - aux(1, i, j))
                        if (q(1, i, j) > 0.d0) then
                            total_mass = total_mass + deta * aux(2, i, j)
                            deta = A * exp(-((x - x_c)**2 + (y - y_c)**2) / sigma**2)
                            q(1, i, j) = q(1, i, j) + deta
                        end if
                    end if
                end if
            end do
        end do
    end do

    print *, "Total mass addition = ", total_mass

end subroutine qinit
