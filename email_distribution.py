/************** CONFIG **************/
var SHEET_NAME = "Emails";
var SPREADSHEET_ID = "1yyRGdlopK6fOz8Vb36B3VEUrrJBgK-8ZfkcQuUfMd2I";

/**
 * REQUIRED for triggers.
 * Paste your Spreadsheet ID (the part between /d/ and /edit in the URL).
 */


// Columns (1-indexed)
var COL_TO = 1;       // A
var COL_SUBJECT = 2;  // B
var COL_BODY = 3;     // C
var COL_STATUS = 4;   // D
var COL_SENT_AT = 5;  // E
var COL_ERROR = 6;    // F
var COL_FILE_URL = 7; // G

// Optional: Drive folder ID to save PDFs in a folder (leave "" to save in My Drive root)
var REPORTS_FOLDER_ID = "";

// Trigger frequency (polling)
var TRIGGER_EVERY_MINUTES = 1;

// Status rules
var STATUS_SENT = "SENT";
var STATUS_ERROR = "ERROR";
var STATUS_PENDING = "PENDING"; // optional value you can use

/************** MENU **************/
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu("Mailer")
    .addItem("Send pending now", "sendPendingEmailsAuto")
    .addItem("Install auto-send (every " + TRIGGER_EVERY_MINUTES + " min)", "installAutoSendTrigger")
    .addItem("Remove mail triggers", "removeMailTriggers")
    .addToUi();
}

/************** TRIGGERS **************/
function installAutoSendTrigger() {
  removeMailTriggers(); // remove duplicates first
  ScriptApp.newTrigger("sendPendingEmailsAuto")
    .timeBased()
    .everyMinutes(TRIGGER_EVERY_MINUTES)
    .create();
}

function removeMailTriggers() {
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i++) {
    var fn = triggers[i].getHandlerFunction();
    if (fn === "sendPendingEmailsAuto" || fn === "sendPendingEmailsAsPdfReport" || fn === "sendPendingEmails") {
      ScriptApp.deleteTrigger(triggers[i]);
    }
  }
}

/************** MAIN AUTO SENDER **************/
function sendPendingEmailsAuto() {
  var lock = LockService.getScriptLock();
  if (!lock.tryLock(20000)) return;

  try {
    if (!SPREADSHEET_ID || SPREADSHEET_ID === "PASTE_YOUR_SHEET_ID_HERE") {
      throw new Error("Set SPREADSHEET_ID at top of Code.gs");
    }

    var ss = SpreadsheetApp.openById(SPREADSHEET_ID);
    var sh = ss.getSheetByName(SHEET_NAME);
    if (!sh) throw new Error("Sheet not found: " + SHEET_NAME);

    var lastRow = sh.getLastRow();
    if (lastRow < 2) return;

    // Ensure at least 7 columns exist
    if (sh.getMaxColumns() < 7) {
      sh.insertColumnsAfter(sh.getMaxColumns(), 7 - sh.getMaxColumns());
    }

    var values = sh.getRange(2, 1, lastRow - 1, 7).getValues();
    var now = new Date();

    for (var i = 0; i < values.length; i++) {
      var rowIndex = i + 2;

      var to = String(values[i][COL_TO - 1] || "").trim();
      var subject = String(values[i][COL_SUBJECT - 1] || "").trim();
      var body = String(values[i][COL_BODY - 1] || "").trim();
      var statusRaw = String(values[i][COL_STATUS - 1] || "").trim();
      var status = statusRaw.toUpperCase();

      // AUTO RULE:
      // Send if status is blank OR PENDING.
      // Skip if SENT or ERROR (don’t spam).
      var shouldSend = (status === "" || status === STATUS_PENDING);
      if (!shouldSend) continue;
      if (!to || to.indexOf("@") === -1) continue;
      if (!subject || !body) continue;

      // Mark as PENDING immediately to prevent duplicates if trigger overlaps
      sh.getRange(rowIndex, COL_STATUS).setValue(STATUS_PENDING);

      try {
        // Create PDF blob
        var pdfBlob = buildPdfBlob_(subject, body, now);

        // Save to Drive and generate link
        var file = savePdfToDrive_(pdfBlob);
        var fileUrl = "https://drive.google.com/file/d/" + file.getId() + "/view";

        // Send email
        var emailBody =
          body +
          "\n\n---\nPDF attached.\nDrive link: " +
          fileUrl;

        MailApp.sendEmail({
          to: to,
          subject: subject,
          body: emailBody,
          attachments: [pdfBlob]
        });

        // Mark SENT
        sh.getRange(rowIndex, COL_STATUS).setValue(STATUS_SENT);
        sh.getRange(rowIndex, COL_SENT_AT).setValue(new Date());
        sh.getRange(rowIndex, COL_ERROR).setValue("");
        sh.getRange(rowIndex, COL_FILE_URL).setValue(fileUrl);

      } catch (e) {
        markError_(sh, rowIndex, String(e && e.message ? e.message : e));
      }
    }
  } finally {
    lock.releaseLock();
  }
}

/************** HELPERS **************/
function buildPdfBlob_(subject, body, now) {
  var html =
    '<div style="font-family:Arial, sans-serif; padding:24px;">' +
      '<h2 style="margin:0 0 6px 0;">' + escapeHtml_(subject) + '</h2>' +
      '<div style="color:#666; font-size:12px; margin-bottom:16px;">' +
        'Generated: ' + escapeHtml_(now.toString()) +
      '</div>' +
      '<hr/>' +
      '<pre style="white-space:pre-wrap; font-size:13px; line-height:1.4;">' +
        escapeHtml_(body) +
      '</pre>' +
    '</div>';

  var blob = HtmlService.createHtmlOutput(html).getAs(MimeType.PDF);

  var safeName =
    "Opal Report - " +
    sanitizeFileName_(subject) +
    " - " +
    Utilities.formatDate(now, Session.getScriptTimeZone(), "yyyy-MM-dd_HH-mm-ss") +
    ".pdf";

  blob.setName(safeName);
  return blob;
}

function savePdfToDrive_(pdfBlob) {
  if (REPORTS_FOLDER_ID && String(REPORTS_FOLDER_ID).trim()) {
    var folder = DriveApp.getFolderById(String(REPORTS_FOLDER_ID).trim());
    return folder.createFile(pdfBlob);
  }
  return DriveApp.createFile(pdfBlob);
}

function markError_(sh, rowIndex, msg) {
  sh.getRange(rowIndex, COL_STATUS).setValue(STATUS_ERROR);
  sh.getRange(rowIndex, COL_ERROR).setValue(msg);
}

function sanitizeFileName_(s) {
  return String(s || "Report")
    .replace(/[\\/:*?"<>|]+/g, " ")
    .trim()
    .substring(0, 80);
}

function escapeHtml_(s) {
  return String(s || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}
{
  "timeZone": "Asia/Kolkata",
  "exceptionLogging": "STACKDRIVER",
  "oauthScopes": [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/script.scriptapp",
    "https://www.googleapis.com/auth/script.send_mail"
  ],
  "runtimeVersion": "V8"
}