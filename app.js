document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("comic-form");
  const button = document.getElementById("submit-button");

  if (form && button) {
    form.addEventListener("submit", () => {
      button.disabled = true;
      button.textContent = "Creating comic…";
    });
  }
});

  const downloadButton = document.getElementById("download-pdf");
  if (downloadButton) {
    downloadButton.addEventListener("click", async () => {
      const original = downloadButton.textContent;
      downloadButton.disabled = true;
      downloadButton.textContent = "Preparing PDF…";

      try {
        const response = await fetch(downloadButton.dataset.downloadUrl);
        if (!response.ok) throw new Error("PDF download failed.");
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const anchor = document.createElement("a");
        anchor.href = url;
        anchor.download = "comiccraft-comic.pdf";
        document.body.appendChild(anchor);
        anchor.click();
        anchor.remove();
        URL.revokeObjectURL(url);

        const pdf = encodeURIComponent(downloadButton.dataset.downloadUrl.split("path=")[1] || "");
        window.location.href = `/export-success?pdf=${pdf}`;
      } catch (error) {
        alert(error.message);
        downloadButton.disabled = false;
        downloadButton.textContent = original;
      }
    });
  }
