async function mergeFiles() {
  const type = document.getElementById("typeSelect").value;
  const input = document.getElementById("fileInput");
  const status = document.getElementById("status");

  if (!input.files.length) {
    alert("Select at least one file.");
    return;
  }

  const formData = new FormData();
  for (let i = 0; i < input.files.length; i++) {
    formData.append("files", input.files[i]);
  }
  formData.append("type", type);

  status.textContent = "Uploading & merging...";

  try {
    const res = await fetch("/merge", {
      method: "POST",
      body: formData
    });

    if (!res.ok) {
      const err = await res.json();
      status.textContent = "Error: " + err.error;
      return;
    }

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "merged." + (type === "audio" ? "mp3" : "mp4");
    a.click();
    status.textContent = "Download started.";
  } catch (err) {
    status.textContent = "Error: " + err.message;
  }
}
