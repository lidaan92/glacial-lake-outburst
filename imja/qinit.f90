
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

        ! Is this a region that should be set?
        logical :: init_region
        integer :: init_type

        ! Region specification
        real(kind=8) :: lower(2)
        real(kind=8) :: upper(2)

    end type lake_region

    type(lake_region), allocatable :: lake_regions(:), cutout_regions(:)

    ! Locals
    integer :: i, j, n, k, region
    integer :: num_regions, num_cutouts
    real(kind=8) :: xm, x, xp, ym, y, yp, x_c, y_c
    real(kind=8) :: sigma, deta, A, theta, total_mass
    logical :: cutout, init_cell

    ! Lake Regions - Data for setting lake_level
    num_regions = 1
    allocate(lake_regions(num_regions))

    lake_regions(1)%lake_level = 5000.d0
    lake_regions(1)%init_region = .true.
    lake_regions(1)%init_type = 2
    lake_regions(1)%lower = [491100.d0, 3085150.d0]
    lake_regions(1)%upper = [493800.d0, 3086400.d0]

    ! lake_regions(2)%lower = [491000.d0, 3086950.d0]
    ! lake_regions(2)%upper = [491900.d0, 3087250.d0]
    ! lake_regions(2)%init_region = .false.

    ! lake_regions(3)%lower = [490750.d0, 3086800.d0]
    ! lake_regions(3)%upper = [491400.d0, 3087250.d0]
    ! lake_regions(3)%init_region = .false.

    ! Symmetric Gaussian hump (type 1)
    !  A = amplitude
    !  sigma = std. dev.
    !  (x_c, y_c) = center
    ! Plane-wave, Gaussian (type 2)
    !  A = amplitude
    !  sigma = std. dev.
    !  (x_c, y_c) = center
    !  theta = angle from x-axis
    
    ! Case 0 (no IC)
    A = 0.d0
    sigma = 0.d0
    x_c = 0.d0
    y_c = 0.d0
    theta = 0.d0

    ! case 1
    ! A = 100.d0
    ! sigma = 100.d0
    ! x_c = 493300.d0
    ! y_c = 3086700.d0
    ! theta = 1.570796327d0 ! pi / 2

    ! Case 2
    ! A = 100.d0
    ! sigma = 100.d0
    ! x_c = 491635.d0
    ! y_c = 3086700.d0
    ! theta = 1.570796327d0 ! pi / 2
    
    ! Set everything to zero
    q = 0.d0
    total_mass = 0.d0

    ! Loop through locations and set anything below given 
    do j = 1, my
        ym = ylower + j * dy
        y = ylower + (j - 0.5d0) * dy
        yp = ylower + (j + 1.d0) * dy
        do i = 1, mx
            xm = xlower + i * dx
            x = xlower + (i - 0.5d0) * dx
            xp = xlower + (i + 1.d0) * dx

            init_cell = .false.
            region = 0
            do n = 1, num_regions
                if (lake_regions(n)%lower(1) <= xm .and.            &
                    xp <= lake_regions(n)%upper(1) .and.            &
                    lake_regions(n)%lower(2) <= ym .and.            &
                    yp <= lake_regions(n)%upper(2)) then

                    init_cell = lake_regions(n)%init_region

                    if (init_cell) then
                        region = n
                    else
                        exit
                    end if
                end if
            end do

            if (init_cell) then
                q(1, i, j) = max(0.d0, lake_regions(region)%lake_level &
                             - aux(1, i, j))
                if (q(1, i, j) > 0.d0) then
                    deta = 0.d0
                    select case(lake_regions(region)%init_type)
                        ! Gaussian
                        case(1)
                            deta = A * exp(-((x - x_c)**2 + (y - y_c)**2) / sigma**2)
                        case(2)
                            ! TODO:  Implement theta
                            deta = A * exp(-(x - x_c)**2 / sigma**2)
                    end select
                    q(1, i, j) = q(1, i, j) + deta
                    total_mass = total_mass + deta * dx * dy
                end if
            end if

        end do
    end do

    print *, "Total mass addition = ", total_mass

end subroutine qinit