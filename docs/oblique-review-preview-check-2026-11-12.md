# Generated review preview check

Double-click `preview_oblique_review.cmd` in the project folder. It opens your normal browser and keeps a local server window open. This uses two artificial colour patterns, no photographs or model fitting. Existing preview answers are preserved on reopening.

1. Confirm the GENERATED UI TEST notice and A/B patterns appear. Browser and resolution fill automatically; enter your OS scale, or `unknown`. Colour settings may stay `unknown`.
2. On case 1, choose any identity answer and enter `preview test` as the reason. Click **Save ratings**. Confirm it says **Saved 1/2 ratings to disk**.
3. Click **Next**. Choose any preference and artifact answer. Click **Save ratings**. Confirm **Saved 2/2 ratings to disk** and **All ratings saved**.
4. Click **Reload saved ratings**, then refresh the browser. Confirm both cases' answers remain when you navigate between them.
5. Click **Download saved JSON**. Confirm a JSON file downloads and contains your two answers. Click **Native 100%** and check the patterns remain visible and equally sized.

Leave the server window open during testing. Afterwards you can close the tab and stop the server with Ctrl+C in its window. Saved revisions stay under `outputs/oblique_review_generated_preview_v1/ratings`; the downloaded JSON is a separate copy.

Tell us whether save, reload/refresh and download worked, or name the failed step. This is a UI check only; the answers must never join the 44-case scientific comparison. No ChatGPT desktop app or extension is required. Actual researcher display details will be recorded again on the real review, not inferred from this preview.
