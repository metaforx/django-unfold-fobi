$(document).ready(function () {
    if (!$('#tabs').length) {
        return;
    }

    function destroyJqueryTabs() {
        if ($.fn.tabs && $('#tabs').data('ui-tabs')) {
            $('#tabs').tabs('destroy');
        }

        $('#tabs')
            .removeClass('ui-tabs ui-widget ui-widget-content ui-corner-all');
        $('#tabs .ui-tabs-nav')
            .removeClass('ui-tabs-nav ui-helper-reset ui-helper-clearfix ui-widget-header ui-corner-all');
        $('#tabs .ui-tabs-panel')
            .removeClass('ui-tabs-panel ui-widget-content ui-corner-bottom');
        $('#tabs .ui-tabs-anchor')
            .removeClass('ui-tabs-anchor');
        $('#tabs li')
            .removeClass('ui-state-default ui-corner-top ui-state-active ui-tabs-active');
    }

    function activateTab(hash) {
        if (!hash) {
            return;
        }

        $('#tabs-items li').removeClass('active').attr('aria-selected', 'false');
        $('#tabs-items a').attr('aria-selected', 'false');

        const $link = $('#tabs-items a[href="' + hash + '"]');
        const $item = $link.closest('li');
        $item.addClass('active').attr('aria-selected', 'true');
        $link.attr('aria-selected', 'true');

        $('#tabs .col').hide();
        $(hash).show();
    }

    function syncActiveTab() {
        const hash = window.location.hash || $('#tabs-items a').first().attr('href');
        activateTab(hash);
    }

    destroyJqueryTabs();
    syncActiveTab();

    $('#tabs-items').on('click', 'a', function (event) {
        event.preventDefault();
        const hash = $(this).attr('href');
        if (hash) {
            window.location.hash = hash;
            activateTab(hash);
        }
    });
});
