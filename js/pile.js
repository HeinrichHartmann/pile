//
// Debug Helper
//

function P(s, t, u) {
  console.log(s, t, u);
}


const TARGETS = [
  { "name" : "Trash",    "target" : "~/Trash",     "key" : "x" },
  { "name" : "Docs",     "target" : "~/Documents", "key" : "1" },
  { "name" : "Books",    "target" : "~/Books",     "key" : "2" },
  { "name" : "Articles", "target" : "~/Articles",  "key" : "3" },
  { "name" : "Tax",      "target" : "~/Tax",       "key" : "4" },
  { "name" : "Pictures", "target" : "~/Pictures",  "key" : "5" },
]

const EXT_IFRAME = [ ".pdf" ]
const EXT_IMG  = [ ".png", ".jpeg" ]
const EXT_PRE  = [ ".txt", ".md" ]

function preview(rec) {
  url = "/pfile/" + encodeURIComponent(rec.filename);
  P(url)
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
// Data Join
//
ctarget = false;
cfilename = false;

function update() {
  $.get("/app/last", (rec, status) => {
    preview(rec);
    var tag_str = [].concat(
      rec.tags.map(function(x) {return "#" + x; }),
      Object.keys(rec.kvtags).map(function(x) { return "#" + x + "=" + rec.kvtags[x]; })
    ).join(", ");
    $("#title h1").text(rec.filename);
    $("#f_date").val(rec.date);
    $("#f_tags").val(rec.tag_str);
    $("#f_title").val(rec.title);
    cfilename = rec.filename;
  })
}


function main() {
  update()

  d3.select("#f_targets")
    .selectAll("input")
    .data(TARGETS)
    .enter()
    .append("input")
    .classed("target_button", true)
    .attr("type", "submit")
    .attr("value", function(d, i) { return `(${d.key})  ${d.name}` })
    .on("click", function(d,i) { ctarget = d.target })
    .each(function(d) { d.input = this })

  $("#form").submit(function( event ) {
    payload = {
      "source" : cfilename,
      "target" : ctarget,
      "meta"   : {
        'date' : $("#f_date").val(),
        'tags' : $("#f_tags").val().split(/[ ]+/).filter(s => (s != "")),
        'title' : $("#f_title").val(),
      }
    }
    $.ajax({
      url: '/app/refile',
      type: 'POST',
      data: JSON.stringify(payload),
      contentType: 'application/json; charset=utf-8',
      dataType: 'json'
    }).done(function(d) {
      $("#log").text(`Wrote ${ d.path }`);
      update();
    }).fail(function() {
      alert("failed!");
    });

    event.preventDefault();
  });

  $(document).keydown(function(e) {
    TARGETS.forEach((target) => {
      if(e.ctrlKey && e.key == target.key) {
        // simulate click event
        target.input.click()
      }
    })
  })

};


$(document).ready(main)
