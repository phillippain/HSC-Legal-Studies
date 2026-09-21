/**
 * Evidence Finder — keep the site's Drive links current, automatically.
 * ---------------------------------------------------------------------------
 * The site links every document to its Google Drive copy, so it needs each
 * file's Drive id. This script records them:
 *
 *   drive-links.json   every file in  Evidence Finder / library   (path -> id)
 *   inbox-links.json   every file in  Evidence Finder / inbox     (name -> id)
 *
 * Both land in the Evidence Finder folder, where Claude reads them when it
 * files new evidence. A file keeps its id when it is moved inside the shared
 * drive, so an id seen in the inbox is still right once the file is filed.
 *
 * ONE-TIME SET-UP (about two minutes)
 *   1. script.google.com  ->  open the project you used before (or New project)
 *   2. Paste this whole file over what is there, and Save.
 *   3. Choose `installTriggers` in the function dropdown and press Run.
 *      Allow the permissions it asks for.
 *   That's all. From then on, without anyone pressing anything:
 *     - every 5 minutes it notes what is sitting in the inbox (a second or two);
 *     - every night it re-maps the whole library, as a safety net for anything
 *       added, renamed or moved by hand.
 *   `mapDriveIds` can still be run by hand at any time. `removeTriggers` turns
 *   the automation off again.
 *
 * If the library is big enough to hit Apps Script's 6-minute limit, a run stops
 * early and schedules itself to carry on a minute later, as often as needed.
 */

// The Evidence Finder folder's id: open it in Drive in a browser, and it is the
// long code at the end of the address — drive.google.com/drive/folders/THIS_PART.
// Left empty, the script finds the folder by name (it must contain `library`).
var ROOT_ID = '';
var ROOT_NAME = 'Evidence Finder';
var LIBRARY_NAME = 'library';      // the filed documents
var INBOX_NAME = 'inbox';          // where new documents are dropped
var OUT_NAME = 'drive-links.json';
var INBOX_OUT = 'inbox-links.json';
var TIME_BUDGET_MS = 4.5 * 60 * 1000;   // stop before Apps Script kills the run

// ------------------------------------------------------------------ library

function mapDriveIds() {
  var t0 = Date.now();
  var props = PropertiesService.getScriptProperties();
  var state = JSON.parse(props.getProperty('state') || 'null');

  var root = rootFolder_();
  if (!state) Logger.log('Walking ' + root.getName() + ' — ' + root.getUrl());

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
      // carry on by itself in a minute, so the nightly run needs nobody
      scheduleResume_();
      Logger.log('RESUME — ' + seen + ' files so far, ' + queue.length +
                 ' folders left. Continuing automatically in a minute.');
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

  var out = writeJson_(root, OUT_NAME, {
    generated: new Date().toISOString(),
    root: ROOT_NAME + '/' + LIBRARY_NAME,
    count: seen,
    files: map
  });
  props.deleteProperty('state');
  clearOneOffs_();
  Logger.log('DONE — ' + seen + ' files mapped. Wrote ' + OUT_NAME + ' — ' + out.getUrl());
}

/** Start again from scratch if a resume ever gets stuck. */
function resetMapDriveIds() {
  PropertiesService.getScriptProperties().deleteProperty('state');
  clearOneOffs_();
  Logger.log('Reset. Run mapDriveIds again.');
}

// -------------------------------------------------------------------- inbox

/* Cheap: one folder, no recursion. Also creates the inbox the first time.
   Writes only when the inbox has changed, so Drive is not churned every 5 min. */
function mapInbox() {
  var root = rootFolder_();
  var inbox = childFolder_(root, INBOX_NAME) || root.createFolder(INBOX_NAME);
  var files = {}, n = 0;
  var queue = [[inbox, '']];
  while (queue.length) {                       // a dropped folder is fine too
    var job = queue.shift(), it = job[0].getFiles();
    while (it.hasNext()) {
      var f = it.next();
      files[job[1] + f.getName()] = {id: f.getId(), mime: f.getMimeType(),
                                     bytes: f.getSize(), added: f.getDateCreated().toISOString()};
      n++;
    }
    var subs = job[0].getFolders();
    while (subs.hasNext()) { var s = subs.next(); queue.push([s, job[1] + s.getName() + '/']); }
  }
  var sig = JSON.stringify(Object.keys(files).sort().map(function (k) { return k + '=' + files[k].id; }));
  var props = PropertiesService.getScriptProperties();
  if (props.getProperty('inboxSig') === sig && root.getFilesByName(INBOX_OUT).hasNext()) return;
  writeJson_(root, INBOX_OUT, {generated: new Date().toISOString(), count: n, files: files});
  props.setProperty('inboxSig', sig);
  Logger.log('Inbox: ' + n + ' file(s).');
}

// ----------------------------------------------------------------- triggers

function installTriggers() {
  removeTriggers();
  ScriptApp.newTrigger('mapInbox').timeBased().everyMinutes(5).create();
  ScriptApp.newTrigger('mapDriveIds').timeBased().everyDays(1).atHour(2).create();
  mapInbox();                     // creates the inbox folder now
  mapDriveIds();                  // and brings the library map up to date
  Logger.log('Installed: inbox every 5 minutes, full library nightly around 2am.');
}

function removeTriggers() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    var fn = t.getHandlerFunction();
    if (fn === 'mapInbox' || fn === 'mapDriveIds') ScriptApp.deleteTrigger(t);
  });
}

// --------------------------------------------------------------------- bits

/* The resume triggers are one-off `after()` triggers; tidy them away once a
   walk finishes so they do not pile up. The recurring ones are left alone. */
function clearOneOffs_() {
  var props = PropertiesService.getScriptProperties();
  var ids = JSON.parse(props.getProperty('oneOffs') || '[]');
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (ids.indexOf(t.getUniqueId()) >= 0) ScriptApp.deleteTrigger(t);
  });
  props.deleteProperty('oneOffs');
}

function scheduleResume_() {
  var t = ScriptApp.newTrigger('mapDriveIds').timeBased().after(60 * 1000).create();
  var props = PropertiesService.getScriptProperties();
  var ids = JSON.parse(props.getProperty('oneOffs') || '[]');
  ids.push(t.getUniqueId());
  props.setProperty('oneOffs', JSON.stringify(ids));
}

function rootFolder_() {
  var root = ROOT_ID ? DriveApp.getFolderById(ROOT_ID) : findFolder_(ROOT_NAME);
  if (!root) throw new Error('Could not find a folder named "' + ROOT_NAME +
    '" containing "' + LIBRARY_NAME + '". Paste its id into ROOT_ID at the top.');
  return root;
}

/* By name, and only a folder that actually holds a `library` subfolder — so a
   stray "Evidence Finder" folder elsewhere in Drive is skipped rather than used.
   If more than one qualifies, it says so instead of guessing. */
function findFolder_(name) {
  var it = DriveApp.getFoldersByName(name), hits = [];
  while (it.hasNext()) {
    var f = it.next();
    if (childFolder_(f, LIBRARY_NAME)) hits.push(f);
  }
  if (hits.length > 1) {
    throw new Error(hits.length + ' folders called "' + name + '" contain a library ' +
      'folder: ' + hits.map(function (f) { return f.getUrl(); }).join('  ') +
      '  Paste the right one\'s id into ROOT_ID.');
  }
  return hits.length ? hits[0] : null;
}

function childFolder_(parent, name) {
  var it = parent.getFoldersByName(name);
  return it.hasNext() ? it.next() : null;
}

function writeJson_(folder, name, obj) {
  var body = JSON.stringify(obj, null, 1);
  var existing = folder.getFilesByName(name);
  if (existing.hasNext()) {
    var f = existing.next();
    f.setContent(body);
    return f;
  }
  return folder.createFile(name, body, MimeType.PLAIN_TEXT);
}
