var itemTpl = null;

function tokenize_template()
{
    itemTpl = $('script[data-template="listitem"]').text().split(/\$\{(.+?)\}/g);
}

function render(props)
{
    return function(tok, i) { return (i % 2) ? props[tok] : tok; };
}

function queryFail()
{
    alert("Data request failed");
}

function querySuccess(json_data)
{
    if (!json_data.retval) {
        alert(json_data.msg);
    }
    else {
        $('#sheets_list').append(json_data.data.map(function (json_data) {
            return itemTpl.map(render(json_data)).join('');
        }));
    }
}

function submit_query(form)
{
    const request_url = "http://127.0.0.1:5000/api/music_sheet/search"  // window.location.origin + "/api/music_sheet/search"
    console.log(request_url)
    var title = document.getElementById("title").value;
    var composer = document.getElementById("composer").value;
    var arranger = document.getElementById("arranger").value;
    var date_added_min = document.getElementById("date_added_min").value;
    var date_added_max = document.getElementById("date_added_max").value;
    json_data = {"data":[{"arranger":"arranger","composer":"composer","date_added":"19-01-2019","instruments":[],"title":"title"},{"arranger":"arranger1","composer":"composer1","date_added":"19-01-2019","instruments":[],"title":"title1"}],"msg":"","retval":true};
    querySuccess(json_data);
    // $.ajax(
    //     { url : request_url,
    //       cache : false,
    //       dataType : "json",
    //       data : {title : title,
    //               composer : composer,
    //               arranger : arranger,
    //               date_added_min : date_added_min,
    //               date_added_max : date_added_max},
    //       method : "POST",
    //       success : querySuccess,
    //       error : queryFail
    //     }
    // );
}

$(document).ready(tokenize_template());
