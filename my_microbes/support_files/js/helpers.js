/*
 * Misc. javascript helper functions used throughout the project.
 *
 * Author: Jai Ram Rideout
 */

/*
 * This function accepts a dialog id as a parameter, and opens the dialog
 * box that is bound to that id. A second optional parameter, target, is
 * the id of the element where the dialog should appear next to. If this
 * parameter is null, the dialog will open at its default location,
 * according to its configured options.
 *
 * For example, if the user clicks a link to view more info, the dialog
 * should appear next to that link, instead of appearing in a location
 * relative to the dialog element, which is hidden. Therefore, the id of
 * the link that opens the dialog should be supplied as the second
 * parameter.
 */
function openDialog(dialog, target) {
  var dialogId = "#" + dialog;

  if (typeof(target) != "undefined") {
    var targetId = "#" + target;
    var scrollOffsets = getScrollXY();

    // Move a little to the left.
    var leftPos = ($(targetId).position().left - scrollOffsets[0] + 95);
    var topPos = ($(targetId).position().top - scrollOffsets[1]);

    $(dialogId).dialog("option", "position", [leftPos, topPos]);
  }

  $(dialogId).dialog("open");
}

/*
 * Returns an array with the scrolling offsets (useful for displaying
 * tooltips/dialogs in the same place even when the user has scrolled on
 * the page and then opens a new dialog).
 *
 * Returns [scrollOffsetX, scrollOffsetY]. This function works in all
 * browsers.
 *
 * Code taken from: http://stackoverflow.com/a/745126
 */
function getScrollXY() {
  var scrOfX = 0, scrOfY = 0;
  if (typeof(window.pageYOffset) == 'number') {
    // Netscape compliant.
    scrOfY = window.pageYOffset;
    scrOfX = window.pageXOffset;
  }
  else if (document.body && (document.body.scrollLeft ||
                             document.body.scrollTop)) {
    // DOM compliant.
    scrOfY = document.body.scrollTop;
    scrOfX = document.body.scrollLeft;
  }
  else if (document.documentElement &&
           (document.documentElement.scrollLeft ||
            document.documentElement.scrollTop)) {
    // IE6 standards compliant mode.
    scrOfY = document.documentElement.scrollTop;
    scrOfX = document.documentElement.scrollLeft;
  }

  return [scrOfX, scrOfY];
}

// Taken from qiime.plot_taxa_summary.
function gg(targetq) {
  window.open("http://www.google.com/search?q=" + targetq, 'searchwin');
}

function initializeGlossary() {
  otu_definition_html = "<div id='otu-definition' class='glossary-item' title='Operational Taxonomic Units (OTUs)'><p>An OTU is a functional definition of a taxonomic group, often based on percent identity of the 16S ribosomal RNA (rRNA) gene. In this study, we began with a reference collection of 16S rRNA sequences (derived from the <a href='http://greengenes.secondgenome.com/'>Greengenes database</a>), and each of those sequences was used to define an Opertational Taxonomic Unit. We then compared all of the sequence reads that we obtained in this study (from your microbial communities and everyone else's) to those reference OTUs, and if a sequence read matched one of those sequences at at least 97%% identity, the read was considered an observation of that reference OTU. This process is one strategy for <i>OTU picking</i>, or assigning sequence reads to OTUs.</p></div>";

  $("body").append(otu_definition_html);

  $(".glossary-item").dialog({
    autoOpen: false,
    width: 500,
    height: 'auto',
    buttons: [{
      text: "Close",
      click: function() {$(this).dialog("close");}
    }]
  });

  $(".otus").click(function(event) {
    openDialog("otu-definition", event.target.id);
    return false;
  });
}
