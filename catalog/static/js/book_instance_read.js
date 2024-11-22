import * as pdfjsLib from "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.8.69/pdf.mjs";

window.addEventListener("DOMContentLoaded", (event) => {
  var url = document.getElementById("pdf-url").value;

  pdfjsLib.GlobalWorkerOptions.workerSrc =
    "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.8.69/pdf.worker.mjs";

  var pdfDoc = null,
    pageNum = parseFloat(document.getElementById("bookmark").value) || 1,
    pageRendering = false,
    pageNumPending = null,
    scale = 1,
    canvas1 = document.getElementById("canvas1"),
    canvas2 = document.getElementById("canvas2"),
    ctx1 = canvas1.getContext("2d"),
    ctx2 = canvas2.getContext("2d");

  /**
   * Render a single page
   */
  function renderPage(num, canvas, ctx) {
    return pdfDoc.getPage(num).then(function (page) {
      var viewport = page.getViewport({ scale: scale });
      canvas.height = viewport.height;
      canvas.width = viewport.width;

      var renderContext = {
        canvasContext: ctx,
        viewport: viewport,
      };
      return page.render(renderContext).promise;
    });
  }

  /**
   * Render two pages at once for wider screens or one page for smaller screens
   */
  function renderPages(startPage) {
    pageRendering = true;

    document.querySelectorAll("#canvas1, #canvas2").forEach((canvas) => {
      canvas.classList.add("fade-out");
    });

    document.querySelectorAll(".flip").forEach((flip) => {
      flip.classList.add("start-animation");
    });

    setTimeout(
      () => {
        // Render the left page
        var renderLeft = renderPage(startPage, canvas1, ctx1);

        // Render the right page if the screen is wide enough
        var renderRight = Promise.resolve();
        if (startPage + 1 <= pdfDoc.numPages && window.innerWidth > 1023) {
          renderRight = renderPage(startPage + 1, canvas2, ctx2);
        } else {
          // Clear the second canvas if there is no second page or if the screen is small
          ctx2.clearRect(0, 0, canvas2.width, canvas2.height);
        }

        // Wait for both renderings to complete
        Promise.all([renderLeft, renderRight]).then(function () {
          pageRendering = false;
          if (pageNumPending !== null) {
            renderPages(pageNumPending);
            pageNumPending = null;
          }
        });

        document.querySelectorAll("#canvas1, #canvas2").forEach((canvas) => {
          canvas.classList.remove("fade-out");
        });

        document.querySelectorAll(".flip").forEach((flip) => {
          flip.classList.remove("start-animation");
        });
        // Update the current page number input
        document.getElementById("page_num").value = startPage;
      },
      window.innerWidth > 1023 ? 1000 : 500
    );
  }

  /**
   * Queue the page rendering, render if not already in progress
   */
  function queueRenderPages(num) {
    if (pageRendering) {
      pageNumPending = num;
    } else {
      renderPages(num);
    }
  }

  /**
   * Displays the previous page(s).
   */
  function onPrevPage() {
    if (pageNum <= 1) {
      return;
    }
    document.querySelectorAll(".flip").forEach((flip) => {
      flip.classList.remove("alt");
    });
    pageNum = Math.max(1, pageNum - (window.innerWidth > 1023 ? 2 : 1)); // Move back by 2 pages if wide
    queueRenderPages(pageNum);
  }
  document.getElementById("prev").addEventListener("click", onPrevPage);

  /**
   * Displays the next page(s).
   */
  function onNextPage() {
    if (pageNum >= pdfDoc.numPages) {
      return;
    }
    document.querySelectorAll(".flip").forEach((flip) => {
      flip.classList.add("alt");
    });
    pageNum = Math.min(
      pdfDoc.numPages,
      pageNum + (window.innerWidth > 1023 ? 2 : 1)
    ); // Move forward by 2 pages if wide
    queueRenderPages(pageNum);
  }
  document.getElementById("next").addEventListener("click", onNextPage);

  /**
   * Displays selected page.
   */
  function onSelectedPage() {
    if (this.value > pdfDoc.numPages || this.value < 1) {
      return;
    }
    pageNum = parseFloat(this.value);
    queueRenderPages(pageNum);
  }
  document
    .getElementById("page_num")
    .addEventListener("change", onSelectedPage);

  /**
   * Asynchronously downloads PDF.
   */
  pdfjsLib.getDocument(url).promise.then(function (pdfDoc_) {
    pdfDoc = pdfDoc_;
    document.getElementById("page_count").textContent = pdfDoc.numPages;

    // Initial rendering of the first page
    renderPages(pageNum);
  });

  // Sauvegarde de la page actuelle dans la base de données
  window.addEventListener("beforeunload", function () {
    let csrfTokenValue = document
      .querySelector('meta[name="csrf-token"]')
      .getAttribute("content");

    const request = new Request(document.getElementById("bookmark-url").value, {
      method: "POST",
      body: JSON.stringify({
        current_page: document.getElementById("page_num").value,
      }),
      headers: {
        "X-CSRFToken": csrfTokenValue,
      },
    });
    fetch(request)
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
      })
      .catch((error) => {
        console.log(error);
        alert(
          "La page actuelle n'a pas pu être sauvegardée. Veuillez noter la page de votre livre pour ne pas perdre votre progression."
        );
      });
  });
});
