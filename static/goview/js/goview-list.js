$('#search_projects').on('keyup', function(event){
    var keypressed = event.keyCode || event.which;
    if (keypressed === 13 && $('.goview-project:visible').size() === 1) {
        window.location.href = $($('.goview-project:visible').get(0)).attr('href');
    } else {
        var pattern = $('#search_projects').val().toLowerCase();
        $('.goview-project').each(function(i) {
            if (pattern.length === 0 || $(this).text().toLowerCase().indexOf(pattern) >= 0) {
                $(this).parent().parent().show();
                if (pattern.length !== 0)
                    $(this).addClass('bg-success');
                else
                    $(this).removeClass('bg-success');
             } else {
                 $(this).parent().parent().hide();
             }
        });
    }
});

$('#update_all').click(function() {
    function showInfo(type, text, reload) {
       BootstrapDialog.show({
           type: type,
           title: 'Update request',
           message: text,
           buttons: [
           {
               label: 'Close',
               action: function(dialog){
                   if (reload) {
                      location.reload();
                   } else {
                       dialog.close();
                   }
               }
           }]
       });
    }

    function perform_update() {
        $('#update_all').addClass('disabled');
        $($('#update_all').children()[0]).addClass('glyphicon-repeat-animate');
        $.ajax({
           url: '/update/'
        }).done(function(data) {
           showInfo(BootstrapDialog.TYPE_SUCCESS, "All projects were updated.");
           $($('#update_all').children()[0]).removeClass('glyphicon-repeat-animate');
        }).fail(function(err) {
           showInfo(BootstrapDialog.TYPE_DANGER, "Update request for projects failed - " + err.status + ": " + err.statusText);
           $($('#update_all').children()[0]).removeClass('glyphicon-repeat-animate');
        });
    }

    showInfo(BootstrapDialog.TYPE_PRIMARY, "Update of all projects is scheduled. Feel free to continue browsing.", false);
    perform_update();
})

function sort_list(key) {
    var tbody = $('#project_list').find('tbody');
    var asc;

    if (key === "trend") {
        asc = $('#sort_trend').children(':first').hasClass('glyphicon-sort-by-attributes')
        tbody.find('tr').sort(function(a, b) {
            if (asc) {
                return parseInt($('td:nth-child(3)', b).text(), 10) - parseInt($('td:nth-child(3)', a).text(), 10);
            } else {
                return parseInt($('td:nth-child(3)', a).text(), 10) - parseInt($('td:nth-child(3)', b).text(), 10);
            }
        }).appendTo(tbody);

        if (asc) {
            $('#sort_trend').children(':first').removeClass('glyphicon-sort-by-attributes');
            $('#sort_trend').children(':first').addClass('glyphicon-sort-by-attributes-alt');
        } else {
            $('#sort_trend').children(':first').removeClass('glyphicon-sort-by-attributes-alt');
            $('#sort_trend').children(':first').addClass('glyphicon-sort-by-attributes');
        }
    } else if (key === "project") {
        asc = $('#sort_project').children(':first').hasClass('glyphicon-sort-by-alphabet-alt');
        tbody.find('tr').sort(function(a, b) {
            if (asc) {
                return $('td:nth-child(2)', a).text().localeCompare($('td:nth-child(2)', b).text());
            } else {
                return $('td:nth-child(2)', b).text().localeCompare($('td:nth-child(2)', a).text());
            }
        }).appendTo(tbody);

        if (asc) {
            $('#sort_project').children(':first').removeClass('glyphicon-sort-by-alphabet-alt');
            $('#sort_project').children(':first').addClass('glyphicon-sort-by-alphabet');
        } else {
            $('#sort_project').children(':first').removeClass('glyphicon-sort-by-alphabet');
            $('#sort_project').children(':first').addClass('glyphicon-sort-by-alphabet-alt');
        }
    } else if (key === "repo") {
        tbody.find('tr').sort(function(a, b) {
                return $('td:nth-child(1)', a).children(':first').attr('href')
                   .localeCompare($('td:nth-child(1)', b).children(':first').attr('href'));
        }).appendTo(tbody);
    }
}

$('#sort_trend').click(function() { sort_list("trend"); });
$('#sort_project').click(function() { sort_list("project"); });
$('#sort_repo').click(function() { sort_list("repo"); });
