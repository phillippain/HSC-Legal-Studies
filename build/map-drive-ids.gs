/**
 * Evidence Finder — map every file in the shared drive to its Drive id.
 * ---------------------------------------------------------------------------
 * Run this once after copying documents into
 *     Shared drives / HSC_LS_SSCBWB / Evidence Finder / library
 * and again whenever you add files. It writes drive-links.json into the
 * Evidence Finder folder; give that file to Claude (or drop it in the repo at
 * data/drive-links.json) and every document link on the site becomes a Drive
 * link.
 *
 * HOW TO RUN
 *   1. script.google.com  ->  New project
 *   2. Paste this whole file over whatever is there, and Save.
 *   3. Choose `mapDriveIds` in the function dropdown and press Run.
 *   4. First run only: it asks for permission to see your Drive files. Allow.
 *   5. Watch the Execution log. When it says DONE, the file is in the folder.
 *
 * If the folder is large enough to hit Apps Script's 6-minute limit, the run
 * stops early and says RESUME. Just press Run again — it picks up where it
 * stopped, as many times as needed.
 */

// The folder to walk. Found by name inside the shared drive; change only if you
// rename it.
var ROOT_NAME = 'Evidence Finder';
var LIBRARY_NAME = 'library';      // the subfolder holding the documents
var OUT_NAME = 'drive-links.json';
var TIME_BUDGET_MS = 4.5 * 60 * 1000;   // stop before Apps Script kills the run

function mapDriveIds() {
  var t0 = Date.now();
  var props = PropertiesService.getScriptProperties();
  var state = JSON.parse(props.getProperty('state') || 'null');

  var root = findFolder_(ROOT_NAME);
  if (!root) throw new Error('Could not find a folder named "' + ROOT_NAME +
    '". Check the name, and that this account can see the shared drive.');

  var library = childFolder_(root, LIBRARY_NAME);
  if (!library) throw new Error('No "' + LIBRARY_NAME + '" folder inside ' +
    ROOT_NAME + '. Copy the documents in first.');

  // queue of [folderId, pathPrefix]; map of relative path -> file id
  var queue = state ? state.queue : [[library.getId(), '']];
  var map = state ? state.map : {};
  var seen = state ? state.seen : 0;

  while (queue.length) {
    if (Date.now() - t0 > TIME_BUDGET_MS) {
      props.setProperty('state', JSON.stringify({queue: queue, map: map, seen: seen}));
      Logger.log('RESUME — ' + seen + ' files so far, ' + queue.length +
                 ' folders left. Press Run again.');
      return;
    }
    var job = queue.shift();
    var folder = DriveApp.getFolderById(job[0]);
    var prefix = job[1];

    var files = folder.getFiles();
    while (files.hasNext()) {
      var f = files.next();
      map[prefix + f.getName()] = f.getId();
      seen++;
    }
    var subs = folder.getFolders();
    while (subs.hasNext()) {
      var s = subs.next();
      queue.push([s.getId(), prefix + s.getName() + '/']);
    }
  }

  var payload = {
    generated: new Date().toISOString(),
    root: ROOT_NAME + '/' + LIBRARY_NAME,
    count: seen,
    files: map
  };
  writeJson_(root, OUT_NAME, payload);
  props.deleteProperty('state');
  Logger.log('DONE — ' + seen + ' files mapped. Wrote ' + OUT_NAME + ' into ' +
             ROOT_NAME + '.');
}

/** Start again from scratch if a resume ever gets stuck. */
function resetMapDriveIds() {
  PropertiesService.getScriptProperties().deleteProperty('state');
  Logger.log('Reset. Run mapDriveIds again.');
}

// --------------------------------------------------------------------- bits

function findFolder_(name) {
  var it = DriveApp.getFoldersByName(name);
  return it.hasNext() ? it.next() : null;
}

function childFolder_(parent, name) {
  var it = parent.getFoldersByName(name);
  return it.hasNext() ? it.next() : null;
}

function writeJson_(folder, name, obj) {
  var body = JSON.stringify(obj, null, 1);
  var existing = folder.getFilesByName(name);
  if (existing.hasNext()) {
    existing.next().setContent(body);
  } else {
    folder.createFile(name, body, MimeType.PLAIN_TEXT);
  }
}
