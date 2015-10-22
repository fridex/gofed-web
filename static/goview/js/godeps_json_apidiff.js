/*
 * TODO: get list of all projects
 * TODO: check if a
 * TODO: sorting based on api changes
 * TODO: loading progressbar
 * TODO: show details in a BootstrapDialog
 */

var global_godeps = [];

$.fn.show_apidiff = function(pkg) {
    function show_apidiff_fill_table() {
       var ret = "";

       for (var j = 0; j < project['stats'].length; j++) {
           var stats = project['stats'][j];

           for (var k = 0; k < stats['added'].length; k++)
              ret += '<tr><td><li class="text-success">' + stats['added'][k]['change'] +
                 " (" + stats['added'][k]['package'] + ")</li></td></tr>";

           for (var k = 0; k < stats['modified'].length; k++)
              ret += '<tr><td><li class="text-danger">' + stats['modified'][k]['change'] +
                 " (" + stats['modified'][k]['package'] + ")</li></td></tr>";
       }

       return ret;
    }

    for (var i = 0; i < global_godeps['Deps'].length; i++) {
        if (global_godeps['Deps'][i]['PkgName'] == pkg) {
           project = global_godeps['Deps'][i];
           break;
        }
    }

    BootstrapDialog.show({
        title: 'APIdiff for ' + pkg,
        size: BootstrapDialog.SIZE_WIDE,
        message:  '<table class="table table-striped table-hover">' +
                    '<thead>' +
                      '<tr>' +
                        '<th class="col-md-6">Apidiff Changes</th>' +
                      '</tr>' +
                    '</thead>' +
                    '<tbody' +
                        show_apidiff_fill_table(project) +
                    '</tbody>' +
                  '</table>' +
                  '<a class="pull-right" href="/project/' + pkg + '?filter=commit&from=' +
                    project['data'][1]['commit'] + '&to=' + project['Rev'] + '" target="_blank">More &gt;&gt;</a>',
        buttons: [{
            label: 'Close',
            action: function(dialog){
                dialog.close();
            }
        }]
    });
}

function pkg_name(import_path) {
    var path;

    path = import_path.split('/');
    if (path[0].indexOf('github.com') === 0) {
       return "golang-github-" + path[1] + '-' + path[2];
    } else if (path[0].indexOf('bitbucket.org') === 0) {
       return "golang-bitbucket-" + path[1] + '-' + path[2];
    } else {
       // TODO: implement
       return import_path;
    }
}

function do_end_load(elem) {
   // simply checking for last elem is not suitable here since actions are async
    if (($('#godeps_json_table_errors tr').length + $('#godeps_json_table_unresolved tr').length +
             $('#godeps_json_table_deps tr').length) == global_godeps['Deps'].length)
        $('#load_spinner').css('visibility', 'hidden');
}

function godeps_prepare_data() {
    for (var i = 0; i < global_godeps['Deps'].length; i++) {
        var self = this;
        this.ip = global_godeps['Deps'][i]['ImportPath'];

        $.ajax({
           url: '/rest/fedora-pkgdb/' + global_godeps['Deps'][i]['PkgName'],
           context: global_godeps['Deps'][i]
        })
        .done(function(data) {
                this['data'] = data;
                godeps_json_fill_table(this);
        })
        .fail(function(data) {
            $('#godeps_json_div_unresolved').removeClass('hidden');
            $('#godeps_json_table_unresolved').append('<tr>' +
                  '<td><a href="http://' + this['ImportPath'] + '">' + this['ImportPath'] + '</a></td>' +
                  '<td><span class="text-danger">Error getting Fedora commit:' + data.statusText + '</span></td>' +
                  '</tr>');
            do_end_load();
        })
    }
}

function parse_godeps_json() {
   try {
       global_godeps = $.parseJSON($('#godeps_json').val());
   } catch(err) {
       BootstrapDialog.show({
           type: BootstrapDialog.TYPE_DANGER,
           title: 'Error parsing Godeps.json',
           message: err,
           buttons: [
           {
               label: 'Close',
               action: function(dialog){
                   dialog.close();
               }
           }]
       });

       return false;
   }
   return true;
}

function godeps_json_upload(evt) {
    var file = evt.target.files[0];
    var fr = new FileReader();

    fr.onload = function(f) {
       $('#godeps_json').text(f.target.result);
    };

    fr.readAsText(file);
}

function godeps_json_fill_table(elem) {
     if (elem['data'][1]['error'] === undefined) {
         $.get('/rest/commit/' + elem['PkgName'] + '/' + elem['data'][1]['commit'] + '/' + elem['Rev'] + '/')
             .done(function(data){
                 elem['stats'] = data;
                 var mod = 0;
                 var add = 0;
                 for (var i = 0; i < data.length; i++) {
                    add += data[i]["added"].length;
                    mod += data[i]["modified"].length;

                 }

                $('#godeps_json_div_deps').removeClass('hidden');
                 $('#godeps_json_table_deps').append('<tr>' +
                        '<td><a href="http://' + elem["ImportPath"] + '">' + elem["PkgName"] + '</a></td>' +
                        '<td class="text-center"><span class="text-success">+' + add + '</span>/<span class="text-danger">~' + mod +'</span></td>' +
                        '<td class="text-center"><a onclick="$(this).show_apidiff(\'' + elem["PkgName"] + '\')">Show Details</a></td>' +
                        '</tr>');
             })
             .fail(function(data) {
                 $('#godeps_json_div_errors').removeClass('hidden');
                 $('#godeps_json_table_errors').append('<tr>' +
                       '<td><a href="http://' + elem["ImportPath"] + '">' + elem["PkgName"] + '</a></td>' +
                       '<td><span class="text-danger">Error getting stats: ' + data.statusText + '</span></td>' +
                       '</tr>');
                 do_end_load();
             })
             .always(function() {
                 do_end_load();
             });
     } else {
         $('#godeps_json_div_errors').removeClass('hidden');
         $('#godeps_json_table_errors').append('<tr>' +
               '<td><a href="http://' + elem["ImportPath"] + '">' + elem["PkgName"] + '</a></td>' +
               '<td><span class="text-danger">Error in response: ' + elem['data'][1]['error'] + '</span></td>' +
               '</tr>');
         do_end_load();
     }
}

function show_godeps_json_apidiff() {
   if (global_godeps["GoVersion"] != undefined)
       $('#godeps_json_goversion').text(global_godeps["GoVersion"]);
   else
       $('#godeps_json_goversion').text("Unknown");

   if (global_godeps["ImportPath"] != undefined)
       $('#godeps_json_import_path').text(global_godeps["ImportPath"]);
   else
       $('#godeps_json_import_path').text("Unknown");

   if (global_godeps["Packages"] != undefined) {
       var packages_html = "<ul>"
       $('#godeps_json_packages').text("");
       for (var i = 0; i < global_godeps["Packages"].length; i++) {
          packages_html += "<li>" + global_godeps["Packages"][i] + "</li>";
       }

       packages_html += "</ul>";
       $('#godeps_json_packages').append(packages_html);
   } else {
       $('#godeps_json_packages').children()[0].remove();
       $('#godeps_json_packages').text("Unknown");
   }
}

function get_godeps_pkg_names() {
    for (var i = 0; i < global_godeps["Deps"].length; i++)
        global_godeps["Deps"][i]["PkgName"] = pkg_name(global_godeps["Deps"][i]["ImportPath"]);
}
/* On load */
$('#godeps_json_input').removeClass('hidden');
$('#godeps_json_submit').click(function() {
    global_godeps = [];
    $('#load_spinner').css('visibility', 'visible');
    $('#godeps_json_table_deps').children().remove();
    $('#godeps_json_table_errors').children().remove();
    $('#godeps_json_table_unresolved').children().remove();
    if (parse_godeps_json()) {
        $('#godeps_json_table').removeClass('hidden');
        $('#godeps_json_input').addClass('hidden');

        get_godeps_pkg_names();
        show_godeps_json_apidiff();
        godeps_prepare_data();
    }
});

$('#godeps_json_new_input').click(function() {
    $('#godeps_json_table').addClass('hidden');
    $('#godeps_json_input').removeClass('hidden');
});

$('#upload_godeps').on('change', godeps_json_upload);

