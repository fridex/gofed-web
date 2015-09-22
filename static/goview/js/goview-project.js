var commit_data = [];

function get_data(popup_dialog) {
    var last_commit;

    if ($('#scm_log_list').children().last().length !== 0)
       last_commit = $('#scm_log_list').children().last()[0].id
    else
       last_commit = "";

    if ((popup_dialog && commit_data.length === 0) || ! popup_dialog) {
        $.ajax({
           url: '/rest/depth/' + $('#project_id').text() + '/5/' + last_commit,
           context: $('#scm_log_list'),
        }).done(function(data) {
           for (var i = 0; i < data.length; ++i) {
              /* skip first redundant commit, if any */
              if (commit_data.length > 0 && commit_data[commit_data.length - 1]['commit'] == data[i]['commit'])
                  continue;
              commit_data.push(data[i]);
           }
           update_data(popup_dialog);
        }).fail(function(err) {
           BootstrapDialog.show({
               type: BootstrapDialog.TYPE_DANGER,
               title: 'SCM Log',
               message: "Failed to get commit logs for " + $('#project_fullname').text() + " - " + err.status + ": " + err.statusText,
               buttons: [
               {
                   label: 'Close',
                   action: function(dialog){
                       dialog.close();
                   }
               }]
           });
        });
    } else {
        update_data(popup_dialog);
    }
}

function show_load() {
    var spinner = '<div class="col-md-12 text-center" id="load_spinner" style="font-size: 4em">' +
                  '<span class="glyphicon glyphicon-repeat glyphicon-repeat-animate"></span>' +
                  '</div>';


    var graphs = ['#graph_total', '#graph_added', '#graph_modified', '#graph_cpc'];
    for (var i = 0; i < graphs.length; i++) {
        $(graphs[i]).html(spinner);
    }
}

function update_data(popup_dialog) {
    var last_commit;
    var add;
    if ($('#scm_log_list').children().last().length !== 0) {
       last_commit = $('#scm_log_list').children().last()[0].id;
       add = false;
    } else {
       add = true;
    }

    for (var i = 0; i < commit_data.length; ++i) {
        if (add) {
            $('#scm_log_list').append(
                    '<tr data-toggle="tooltip" title="' + commit_data[i]['author'] + '" id="'+ commit_data[i]['commit'] + '">' +
                      '<td class="col-md-1 text-center"><input type="radio" name="from_commit" value="'+ commit_data[i]['commit'] + '" /></td>' +
                      '<td class="col-md-1 text-center"><input type="radio" name="to_commit" value="'+ commit_data[i]['commit'] + '" /></td>' +
                      '<td class="col-md-2">' + commit_data[i]['commit'].substring(0, 7) + '</td>' +
                      '<td class="col-md-5">' + commit_data[i]['commit_msg'] + '</td>' +
                      '<td class="col-md-3 text-center">' + commit_data[i]['date'] + '</td>' +
                    '</tr>'
                  );
        }
        if (commit_data[i]['commit'] === last_commit)
            add = true;
    }

    if ($('#filter_from_commit').val().length >= 4)
        $("input[name=from_commit]:radio").each(function() {
            $(this).attr('checked', $(this).val().indexOf($('#filter_from_commit').val()) === 0);
        });

    if ($('#filter_to_commit').val().length >= 4)
        $("input[name=to_commit]:radio").each(function() {
            $(this).attr('checked', $(this).val().indexOf($('#filter_to_commit').val()) === 0);
        });

    if ($("#scm_log_list input[name=from_commit]:checked").length === 0)
        $('#scm_log_list tr:first input[name=from_commit]').attr('checked', true);

    if ($("#scm_log_list input[name=to_commit]:checked").length === 0)
        $('#scm_log_list tr:last input[name=to_commit]').attr('checked', true);
}

function load_stats() {
   var project_id = $('#project_id').text();
   var filter = $('#filter_type').val()

   function get_query() {
      var res = '/' + filter + '/' + project_id + '/';

      if (filter === 'date') {
         res += $('#filter_from_date').val() + '/' + $('#filter_to_date').val();
      } else if (filter === 'commit') {
         res += $('#filter_from_commit').val() + '/' + $('#filter_to_commit').val();
      } else if (filter === 'depth') {
         res += $('#filter_depth').val() + '/' + $('#filter_from_commit').val();
      }

      return (res + '/graph.svg').replace("//", "/");
   }

   var graphs = ['total', 'added', 'modified', 'cpc']
   for (var i = 0; i < graphs.length; ++i) {
      $.ajax({
         url: '/graph/' + graphs[i] + get_query(),
         context: $('#graph_' + graphs[i]),
         beforeSend: show_load,
      }).done(function(data) {
         var svgNode = $("svg", data);
         var docNode = document.adoptNode(svgNode[0]);
         $(this).html(docNode);
         $(this).removeClass("alert alert-danger text-center");
         init_svg(docNode);
      }).fail(function(err) {
         $(this).addClass("alert alert-danger text-center");
         $(this).text("Failed to retrieve data from server - " + err.status + ": " + err.statusText);
      });
   }
}

function update_info() {
    $.ajax({
       url: '/rest/info/' + $('#project_fullname').text(),
    }).done(function(data) {
       $('#project_update_date').text(data['update']);
       $('#project_trend').text(data['trend']);
    }).fail(function(err) {
       BootstrapDialog.show({
           type: BootstrapDialog.TYPE_DANGER,
           title: 'SCM Log',
           message: "Failed to get updates for " + $('#project_fullname').text() + " - " + err.status + ": " + err.statusText,
           buttons: [
           {
               label: 'Close',
               action: function(dialog){
                   dialog.close();
               }
           }]
       });
    });
}

function site_url() {
    return window.location.href.split(window.location.host)[0] + window.location.host;
}

$('#show_commit').click(function() {
    $.ajax({
       url: '/rest/commit/' + $('#project_fullname').text() + '/' +
          $('#filter_from_commit').val() + '/' + $('#filter_to_commit').val() + '/',
    }).done(function(data) {
        function get_apidiff_ul(data) {
            var str_add = "";
            var str_mod = "";
            for (var i = 0; i < data["modified"].length; ++i) {
                str_add += '<li class="text-danger">' +
                              data["modified"][i]["change"] +
                              ", package: " + data["modified"][i]["package"] +
                            "</li>";
            }
            if (str_add.length != 0)
                 str_add = "<ul>" + str_add + "</ul>";
            for (var i = 0; i < data["added"].length; ++i) {
                str_mod += '<li class="text-success">' +
                              data["added"][i]["change"] +
                              ", package: " + data["added"][i]["package"] +
                            "</li>";
            }
            if (str_mod.length != 0)
                 str_mod = "<ul>" + str_mod + "</ul>";
            return str_add + str_mod;
        }

        var tbl = "";
        var apidiff_ul = "";
        for (var i = 0; i < data.length; ++i) {
            apidiff_ul = get_apidiff_ul(data[i]);
            if (apidiff_ul.length != 0) {
                tbl += '<tr>' +
                         '<td>' + data[i]["commit"].substring(0, 7) + '</td>' +
                         '<td>' + get_apidiff_ul(data[i]) + '</td>' +
                         '<td>' + data[i]["date"] + '</td>' +
                       '</tr>';
            }
        }

        BootstrapDialog.show({
            title: 'Apidiff Log for ' + $('#project_fullname').text(),
            size: BootstrapDialog.SIZE_WIDE,
            data: commit_data,
            onshown: function() { get_data(true) },
            message:  '<table class="table table-striped table-hover">' +
                        '<thead>' +
                          '<tr>' +
                            '<th class="col-md-3">Commit</th>' +
                            '<th class="col-md-6">Apidiff Changes</th>' +
                            '<th class="col-md-3 text-center">Date</th>' +
                          '</tr>' +
                        '</thead>' +
                        '<tbody id="scm_apidiff_list">' +
                            tbl +
                        '</tbody>' +
                      '</table>',
            buttons: [{
                label: 'Close',
                action: function(dialog){
                    dialog.close();
                }
            }]
        });
    }).fail(function(err) {
       BootstrapDialog.show({
           type: BootstrapDialog.TYPE_DANGER,
           title: 'SCM Apidiff',
           message: "Failed to get apidiffs for " + $('#project_fullname').text() + " - " + err.status + ": " + err.statusText,
           buttons: [
           {
               label: 'Close',
               action: function(dialog){
                   dialog.close();
               }
           }]
       });
    });
});

$('#show_log').click(function() {
    function show_apidiff_fired(dialog) {
        $('#filter_type').val('commit');
        $('#filter_type').trigger("change");
        $('#filter_from_commit').val($('input[name=from_commit]:checked', '#apidiff_form').val());
        $('#filter_to_commit').val($('input[name=to_commit]:checked', '#apidiff_form').val());
        // TODO: check if both are clicked
        dialog.close();
        $('#show_stats').trigger('click');
        $('#filter_from_commit').trigger('keyup');
    }

    BootstrapDialog.show({
        title: 'SCM Log for ' + $('#project_fullname').text(),
        size: BootstrapDialog.SIZE_WIDE,
        data: commit_data,
        onshown: function() { get_data(true) },
        message: '<form id="apidiff_form"><table class="table table-striped table-hover">' +
                    '<thead>' +
                      '<tr>' +
                        '<th class="col-md-1 text-center">From</th>' +
                        '<th class="col-md-1 text-center">To</th>' +
                        '<th class="col-md-2">Commit</th>' +
                        '<th class="col-md-5">Commit message</th>' +
                        '<th class="col-md-3 text-center">Date</th>' +
                      '</tr>' +
                    '</thead>' +
                    '<tbody id="scm_log_list">' +
                    '</tbody>' +
                  '</table></form>',
        buttons: [{
            label: 'Load more',
            action: function() { get_data(false); },
        },
        {
            label: 'Close',
            action: function(dialog){
                dialog.close();
            }
        },
        {
            label: 'Show Apidiff',
            cssClass: 'btn-primary',
            action: function(dialog) { show_apidiff_fired(dialog); },
        }]
    });
});

$('#swap_fields').click(function() {
    if($('#filter_type').val()=='commit') {
        tmp = $('#filter_from_commit').val();
        $('#filter_from_commit').val($('#filter_to_commit').val());
        $('#filter_to_commit').val(tmp);
    } else if ($('#filter_type').val()=='date') {
        tmp = $('#filter_from_date').val();
        $('#filter_from_date').val($('#filter_to_date').val());
        $('#filter_to_date').val(tmp);
    }
});
$('#show_stats').click(function() { load_stats(); });
$('#update').click(function() {
    function showInfo(type, text) {
       BootstrapDialog.show({
           type: type,
           title: 'Update ' + $('#project_fullname').text(),
           message: text,
           buttons: [
           {
               label: 'Close',
               action: function(dialogItself){
                   dialogItself.close();
               }
           }]
       });
    }

    function perform_update() {
        $('#update').addClass('disabled');
        $($('#update').children()[0]).addClass('glyphicon-repeat-animate');
        $.ajax({
           url: '/update/' + $('#project_fullname').text(),
        }).done(function(data) {
           update_info();
           showInfo(BootstrapDialog.TYPE_SUCCESS, "Project " + $('#project_fullname').text() + " was successfully updated.");
           $($('#update').children()[0]).removeClass('glyphicon-repeat-animate');
        }).fail(function(err) {
           showInfo(BootstrapDialog.TYPE_DANGER, "Update request for project " + $('#project_fullname').text() + " failed - " + err.status + ": " + err.statusText);
           $($('#update').children()[0]).removeClass('glyphicon-repeat-animate');
        });
    }

    showInfo(BootstrapDialog.TYPE_PRIMARY, "Update of project " + $('#project_fullname').text() + " is scheduled. Feel free to continue browsing.");
    perform_update();
})


$('#dependency_graph').click(function() {
    window.open(site_url() + '/graph/dependency/' + $('#project_fullname').text() + '/graph.png',
          'liveMatches','directories=no,titlebar=no,toolbar=no,location=no,status=no,menubar=no,scrollbars=no,resizable=yes,fullscreen=yes');
});

$('#query_url').click(function() {
    function showQuery(text) {
       BootstrapDialog.show({
           type: BootstrapDialog.TYPE_PRIMARY,
           title: 'Query URL',
           size: BootstrapDialog.SIZE_WIDE,
           message: '<div class="text-center">' + text + '</div>',
           buttons: [
           {
               label: 'Close',
               cssClass: 'btn-primary',
               action: function(dialogItself){
                   dialogItself.close();
               }
           }]
       });
    }

    var filter_type = $('#filter_type').val();
    var url = site_url() + '/project/' + $('#project_fullname').text() + '?';

    if (filter_type === 'commit') {
       url += 'filter=commit&';
       if ($('#filter_from_commit').val().length !== 0)
           url += 'from=' + $('#filter_from_commit').val().substring(0, 7) + '&';
       if ($('#filter_to_commit').val().length !== 0)
           url += 'to=' + $('#filter_to_commit').val().substring(0, 7);
    } else if (filter_type === 'depth') {
       url += 'filter=depth&';
       if ($('#filter_from_commit').val().length !== 0)
           url += 'from=' + $('#filter_from_commit').val().substring(0, 7) + '&';
       if ($('#filter_depth').val().length !== 0)
           url += 'depth=' + $('#filter_depth').val();
    } else if (filter_type === 'date') {
       url += 'filter=date&';
       if ($('#filter_from_date').val().length !== 0)
           url += 'from=' + $('#filter_from_date').val() + '&';
       if ($('#filter_to_date').val().length !== 0)
           url += 'to=' + $('#filter_to_date').val();
    }

    showQuery(url);
})


$('#filter_type').on('change', function(){
    if($(this).val()=='commit') {
        $('#filter_from_commit').parent().removeClass('hidden');
        $('#filter_to_commit').parent().removeClass('hidden');
        $('#filter_depth').parent().addClass('hidden');
        $('#filter_from_date').parent().addClass('hidden');
        $('#filter_to_date').parent().addClass('hidden');
        $('#swap_fields').removeClass('disabled');
        $('#show_commit').removeClass('disabled');
    } else if ($(this).val()=='depth') {
        $('#filter_from_commit').parent().removeClass('hidden');
        $('#filter_depth').parent().removeClass('hidden');
        $('#filter_to_commit').parent().addClass('hidden');
        $('#filter_from_date').parent().addClass('hidden');
        $('#filter_to_date').parent().addClass('hidden');
        $('#swap_fields').addClass('disabled');
        $('#show_commit').addClass('disabled');
    } else if ($(this).val()=='date') {
        $('#filter_from_date').parent().removeClass('hidden');
        $('#filter_to_date').parent().removeClass('hidden');
        $('#filter_from_commit').parent().addClass('hidden');
        $('#filter_depth').parent().addClass('hidden');
        $('#filter_to_commit').parent().addClass('hidden');
        $('#swap_fields').removeClass('disabled');
        $('#show_commit').addClass('disabled');
    }

    $('#filter_depth').trigger("keyup");
});

function url_param(param) {
    var url_var = window.location.search.substring(1).split('&');

    for (var i = 0; i < url_var.length; i++) {
        var param_name = url_var[i].split('=');
        if (param_name[0] == param)
            return param_name[1];
    }

    return "";
}

function get_url_param() {
    var filter_type = url_param('filter');
    if (filter_type === 'commit') {
        if (url_param('from').length !== 0)
            $('#filter_from_commit').val(url_param('from'));
        if (url_param('to').length !== 0)
            $('#filter_to_commit').val(url_param('to'));
    } else if (filter_type === 'depth') {
        if (url_param('from').length !== 0)
            $('#filter_from_commit').val(url_param('from'));
        if (url_param('depth').length !== 0)
            $('#filter_depth').val(url_param('depth'));
    } else if (filter_type === 'date') {
        if (url_param('from').length !== 0)
            $('#filter_from_date').val(url_param('from'));
        if (url_param('to').length !== 0)
            $('#filter_to_date').val(url_param('to'));
    } else
       return;

    $('#filter_type').val(filter_type);
    $('#filter_type').trigger("change");
}

$(document).ready(function () {
    var opts = {autoclose: true, todayHighlight: true, format: "yyyy-mm-dd"}
    $('#filter_from_date').datepicker(opts);
    $('#filter_to_date').datepicker(opts);
    $('#filter_type').trigger("change");
    get_url_param();
    load_stats();
 });

function toggle_show_button() {
    var filter_type = $('#filter_type').val();
    var title = 'Enter query parameters to query graphs';

    if (filter_type === 'commit') {
        if (($('#filter_from_commit').val().length >= 4
                 && ($('#filter_to_commit').val().length >= 4 || $('#filter_to_commit').val().length === 0))
              || ($('#filter_to_commit').val().length >= 4
                 && ($('#filter_from_commit').val().length >= 4 || $('#filter_from_commit').val().length === 0))) {
            $('#show_stats').parent().attr('title', '');
            $('#show_stats').attr('disabled', false);
            $('#show_commit').attr('disabled', false);
        } else {
            $('#show_stats').parent().attr('title', title);
            $('#show_stats').attr('disabled', true);
            $('#show_commit').attr('disabled', true);
        }
    } else if (filter_type === 'depth') {
        $('#show_commit').attr('disabled', true);
        if ($('#filter_depth').val().length !== 0
              && ($('#filter_from_commit').val().length === 0 || $('#filter_from_commit').val().length >= 4)) {
            $('#show_stats').parent().attr('title', '');
            $('#show_stats').attr('disabled', false);
        } else {
            $('#show_stats').parent().attr('title', title);
            $('#show_stats').attr('disabled', true);
        }
    } else if (filter_type === 'date') {
        // TODO: better check
        $('#show_commit').attr('disabled', true);
        if ($('#filter_from_date').val().length !== 0 || $('#filter_to_date').val().length !== 0) {
            $('#show_stats').parent().attr('title', '');
            $('#show_stats').attr('disabled', false);
        } else {
            $('#show_stats').parent().attr('title', title);
            $('#show_stats').attr('disabled', true);
        }
    }
}

$('#filter_from_commit').on('keyup change', $.proxy(toggle_show_button, this));
$('#filter_to_commit').on('keyup change', $.proxy(toggle_show_button, this));
$('#filter_depth').on('keyup change', $.proxy(toggle_show_button, this));
$('#filter_from_date').on('keyup change', $.proxy(toggle_show_button, this));
$('#filter_to_date').on('keyup change', $.proxy(toggle_show_button, this));
