function setClipboard(value) {
  var tempInput = document.createElement("input");
  tempInput.style = "position: absolute; left: -1000px; top: -1000px";
  tempInput.value = value;
  document.body.appendChild(tempInput);
  tempInput.select();
  document.execCommand("copy");
  document.body.removeChild(tempInput);
}

var recs = [];
var crec = 0;
var selected = [];

function P(s, t, u) {
  console.log(s, t, u);
}

function mod(a, n) {
  var x = a % n;
  while (x < 0) { x += n }
  return x;
}

function select_clear() {
  selected.forEach((sel) => { sel.toggleClass("selected", false) });
  selected = [];
}

EXT_IFRAME = [ ".pdf" ]
EXT_IMG  = [ ".png" ]
EXT_PRE  = [ ".txt", ".md" ]

function select(n) {
  crec = mod(n, recs.length);
  rec = recs[crec]

  select_clear();
  selected.push(
    $(rec.row).toggleClass("selected", true)
  );
  rec.row.scrollIntoViewIfNeeded({block: "start", inline: "nearest"});

  $("#title h1").text(rec.filename);

  url = "/doc/" + encodeURIComponent(rec.filename);
  if ( EXT_IFRAME.includes(rec.extension) ) {
    $("#no_preview").css("display", "none");
    $("#preview_img").css("display", "none");
    $("#preview_pre").css("display", "none");
    $("#preview_iframe").css("display", "block")
      .get(0).contentWindow.location.replace(url);
  }
  else if ( EXT_IMG.includes(rec.extension) ) {
    $("#no_preview").css("display", "none");
    $("#preview_iframe").css("display", "none");
    $("#preview_pre").css("display", "none");
    $("#preview_img").css("display", "block")
      .attr("src", url);
  }
  else if ( EXT_PRE.includes(rec.extension) ) {
    $("#no_preview").css("display", "none");
    $("#preview_iframe").css("display", "none");
    $("#preview_img").css("display", "none");
    pre = $("#preview_pre").css("display", "block");
    pre.text("... loading");
    $.get(url, function(data, status) {
      pre.text(data);
    });
  }
  else {
    $("#preview_iframe").css("display", "none");
    $("#preview_img").css("display", "none");
    $("#preview_pre").css("display", "none");
    $("#no_preview").css("display", "flex");
  }
  setClipboard(rec.filename);
}

function ping() {
  P("ping!");
  $("#table th").toggleClass("ping", true);
  setTimeout(() => {
    $("#table th").toggleClass("ping", false);
  }, 200);
}

function select_next() {
  if (crec > 0) {
    select(crec - 1);
  }
  else {
    ping();
  }
}

function select_prev() {
  if (crec < recs.length - 1) {
    select(crec + 1);
  }
  else {
    ping();
  }
}

function download() {
  var link = document.createElement("a");
  cname = recs[crec].filename;
  path = "/doc/" + encodeURIComponent(cname);
  link.download = cname;
  link.href = path;
  link.click();
}

function main() {
  $.get("/list", function(data, status){
    var table = $("#table")[0];
    data.forEach(function(rec) {
      recs.push(rec);
      const tag_str = [].concat(
        rec.tags.map(function(x) {return "#" + x; }),
        Object.keys(rec.kvtags).map(function(x) { return "#" + x + "=" + rec.kvtags[x]; })
      ).join(", ");
      const row = table.tBodies[0].insertRow(0);
      row.insertCell(0).innerText = rec.date;
      row.insertCell(1).innerText = tag_str;
      row.insertCell(2).innerText = rec.title;
      row.insertCell(3).innerText = rec.extension;
      rec.row = row;
      rec.n = recs.length;
      row.rec = rec;
    });

    $("#table tr").click(function(event) {
      select(this.rec.n);
    });

    const rows = $('#table tbody tr');
    $('#filter').keyup(function() {
      var val = $.trim($(this).val()).replace(/ +/g, ' ').toLowerCase();
      rows.show().filter(function() {
        var text = $(this).text().replace(/\s+/g, ' ').toLowerCase();
        return !~text.indexOf(val);
      }).hide();
    });
    select(recs.length - 1);
  });

  var f_toggle = true;
  $(document).keydown(function(e){
    if(e.ctrlKey && e.key == 'f') {
      if(f_toggle) {
        $('#left').width("0%");
        $('#right').width("100%");
      } else {
        $('#left').width("50%");
        $('#right').width("50%");
      }
      f_toggle = ! f_toggle;
      console.log("toggle fullscreen");
    }
    if(e.ctrlKey && e.key == 'n') {
      select_next();
    }
    if(e.ctrlKey && e.key == 'p') {
      select_prev();
    }
    if(e.ctrlKey && e.key == 'x') {
      download();
    }
  });


};

$(document).ready(main)
