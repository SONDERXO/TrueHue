// An early failure closes only this candidate; saved answers remain downloadable.
async function updateReviewClosure() {
  try {
    const response = await fetch('/review-status');
    if (!response.ok) return;
    const status = await response.json();
    if (!status.closed) return;
    const note = document.getElementById('preview-note');
    note.hidden = false;
    note.textContent = status.message + ' Download the saved JSON to retain your answers.';
    note.style.cssText = 'padding:16px;background:#fff1d6;border:2px solid #a55b00';
    document.getElementById('next').disabled = true;
    document.getElementById('save').disabled = true;
  } catch (_) { /* The existing save controls report connection failures. */ }
}
setInterval(updateReviewClosure, 1000);
updateReviewClosure();
