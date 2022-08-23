//
// Debug Helper
//

function P(s, t, u) {
  console.log(s, t, u);
}

function mod(a, n) {
  var x = a % n;
  while (x < 0) { x += n }
  return x;
}


//
// Helper
//

function setClipboard(value) {
  var tempInput = document.createElement("input");
  tempInput.style = "position: absolute; left: -1000px; top: -1000px";
  tempInput.value = value;
  document.body.appendChild(tempInput);
  tempInput.select();
  document.execCommand("copy");
  document.body.removeChild(tempInput);
}

function download() {
  var link = document.createElement("a");
  cname = recs[crec].path;
  path = "/dfile/" + encodeURIComponent(cname);
  link.download = cname;
  link.href = path;
  link.click();
}

var preview_job = false;
function preview(rec) {
  if (preview_job) {
    clearTimeout(preview_job);
  }
  preview_job = setTimeout(() => {
    do_preview(rec);
  }, 500);
}

function do_preview(rec) {
  url = "/dfile/" + encodeURIComponent(rec.path);
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
}

//
// Selection Logic
//

const EXT_IFRAME = [ ".pdf" ]
const EXT_IMG  = [ ".png" ]
const EXT_PRE  = [ ".txt", ".md", ".sh" ]

var recs = [];
var crec = false;

function select(n) {
  if (crec === n) { return; }
  crec = n
  rec = recs[n];
  console.assert(rec);

  P("select", n, rec)

  if (rec.dom_element && rec.dom_element.scrollIntoViewIfNeeded) {
    rec.dom_element.scrollIntoViewIfNeeded({block: "start", inline: "nearest"});
  }

  $("#title h1").text(rec.filename);
  setClipboard(rec.filename);

  preview(rec);

  update_table();
}

function select_first() {
  crec = -1;
  select_next();
}

function select_next() {
  var n = crec + 1;
  while(n < recs.length && recs[n].hidden) { n++; }
  if (n >= recs.length || (n == recs.length && recs[n].hidden)) {
    ping();
  } else {
    select(n);
  }
}

function select_prev() {
  var n = crec - 1;
  while(n > 0 && recs[n].hidden) { n--; }
  if (n < 0 || (n == 0 && recs[n].hidden)) {
    ping();
  } else {
    select(n);
  }
}

function ping() {
  $("#table th").toggleClass("ping", true);
  setTimeout(() => {
    $("#table th").toggleClass("ping", false);
  }, 200);
}

//
// Instant Filter
//

function filter(event) {
  const pattern = event.currentTarget.value.replace(/ +/g, ' ').toLowerCase();
  recs.forEach((rec, i) => {
    var text = $(rec.dom_element).text().replace(/\s+/g, ' ').toLowerCase();
    if (!~text.indexOf(pattern)) {
      rec.hidden = true
    } else {
      rec.hidden = false
    }
  });
}

//
// Data Join
//

function update_table() {

  var t = d3.transition()
      .duration(150)
      .ease(d3.easeLinear);

  var visible_recs = recs.filter(rec => !rec.hidden)

  var tr = d3.select("#table tbody")
    .selectAll("tr")
      .data(visible_recs, function(rec) {
        return rec ? rec.n : this.rec.n
      });

  tr.exit()
    .transition(t)
    .style("color", "#FFF")
    .remove()

  tr.enter()
    .append("tr")
    .each(function(rec, n) {
        this.rec = rec;
        rec.dom_element = this;
      })
    .on("click", function(d,i) { select(i) })
    .selectAll("td")
    .data(function(rec) { return rec.row })
    .enter()
      .append("td")
    .text(d => { return d })
    .style("color", "#FFF")
    .transition(t)
    .style("color", "#000")

  tr.each(function(rec) {
    $(this).toggleClass("selected", rec.n == crec);
  });

}

function main() {
  $.get("/app/list", (data, status) => {
    data.forEach((rec, n) => {
      rec.n = n;
      rec.hidden = false;
      rec.selected = false;
      rec.tag_str = [].concat(
        rec.tags.map(function(x) {return "#" + x; }),
        Object.keys(rec.kvtags).map(function(x) { return "#" + x + "=" + rec.kvtags[x]; })
      ).join(", ");
      rec.row = [
        rec.date,
        rec.tag_str,
        rec.title,
        rec.extension
      ]
      recs.push(rec);
    });
    select_first();
    update_table();
  });

  $('#filter').keyup((e) => {
    if(e.code == "Escape") {
      return document.activeElement.blur();
    }
    filter(e);
    select_first();
    event.currentTarget.focus();
    update_table();
  });

  var f_toggle = 0;
  $(document).keydown(function(e){
    if(document.activeElement.getAttribute("id") == "filter") { return; }
    if(e.code == "Enter") { return $("#filter").focus();  }
    if(e.key == 'f') {
      if(f_toggle == 0) {
        $('#left').hide();
        $('#left').css({'width': '0%'});
        $('#right').css({'width': '100%'});
      } else if (f_toggle == 1) {
        $('#left').show();
        $('#right').hide();
        $('#left').css({'width': '100%'});
        $('#right').css({'width': '0%'});
      } else if (f_toggle == 2) {
        $('#right').show();
        $('#left').css({'width': '50%'});
        $('#right').css({'width': '50%'});
      }
      f_toggle = (f_toggle + 1) % 3
    }
    if(e.key == 'n' || e.key == "j") {
      select_next();
    }
    if(e.key == 'p' || e.key == "k") {
      select_prev();
    }
    if(e.key == 'x') {
      download();
    }
  });
};

$(document).ready(main)
