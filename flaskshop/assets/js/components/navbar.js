const $toogleIcon = $('.nav_bar__brand__menu-toggle');
const $mobilenav_ = $('nav_');
const $searchIcon = $('.mobile-search-icon');
const $closeSearchIcon = $('.mobile-close-search');
const $searchForm = $('.search-form');

const rendernav_bar = () => {
    const $desktopLinkBar = $('.nav_bar__login');
    const $mobileLinkBar = $('.nav_bar__menu__login');
    const windowWidth = window.innerWidth;
    const $languagePicker = $('.language-picker');

    if (windowWidth < 768) {
        const $desktopLinks = $desktopLinkBar.find('a').not('.dropdown-link');
        if ($desktopLinks.length) {
            $searchForm.addClass('search-form--hidden');
            $mobilenav_.append('<ul class="nav_ nav_bar-nav_ nav_bar__menu__login"></ul>');
            $languagePicker.appendTo('.nav_bar__menu__login')
                .wrap('<li class="nav_-item login-item"></li>')
                .addClass('nav_-link');
            $desktopLinks
                .appendTo('.nav_bar__menu__login')
                .wrap('<li class="nav_-item login-item"></li>')
                .addClass('nav_-link');
            $desktopLinkBar
                .find('li')
                .remove();
        }
    } else {
        const $mobileLinks = $mobileLinkBar.find('a').not('.dropdown-link');
        if ($mobileLinks.length) {
            $searchForm.removeClass('search-form--hidden');
            $languagePicker.appendTo('.nav_bar__login ul')
                .wrap('<li></li>')
                .removeClass('nav_-link');
            $mobileLinks
                .appendTo('.nav_bar__login ul')
                .wrap('<li></li>')
                .removeClass('nav_-link');
            $mobileLinkBar.remove();
        }
    }
};

// -----

rendernav_bar();
$toogleIcon
    .on('click', (e) => {
        $mobilenav_.toggleClass('open');
        e.stopPropagation();
    });
$(document)
    .on('click', () => $mobileNav.removeClass('open'));
$(window)
    .on('resize', renderNavbar);
$searchIcon
    .on('click', () => $searchForm.removeClass('search-form--hidden'));
$closeSearchIcon
    .on('click', () => $searchForm.addClass('search-form--hidden'));
