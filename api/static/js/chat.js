(function () {
  if (!window.api.hasSessionCookie()) {
    window.location.replace(window.PAGES.LOGIN);
    return;
  }

  const logEl = document.getElementById("chat-log");
  const emptyEl = document.getElementById("empty-state");
  const formEl = document.getElementById("chat-form");
  const inputEl = document.getElementById("chat-input");
  const fileEl = document.getElementById("chat-file");
  const sendBtn = document.getElementById("send-btn");
  const logoutBtn = document.getElementById("logout-btn");
  const threadLabel = document.getElementById("thread-label");
  const timerEl = document.getElementById("session-timer");

  // Image preview elements
  const uploadTrigger = document.getElementById("upload-trigger");
  const imgPreviewWrap = document.getElementById("img-preview-wrap");
  const imgPreviewThumb = document.getElementById("img-preview-thumb");
  const imgPreviewName = document.getElementById("img-preview-name");
  const imgRemoveBtn = document.getElementById("img-remove-btn");

  // Thread Label setup
  const threadMatch = document.cookie.split(";").map(function (c) { return c.trim(); })
    .find(function (c) { return c.startsWith("thread_id="); });
  threadLabel.textContent = threadMatch ? threadMatch.split("=")[1].slice(0, 8) + "…" : "none";

  // Countdown timer logic
  let sessionExpiry = localStorage.getItem("session_expiry");
  if (!sessionExpiry) {
    // Default to 5 minutes if missing
    sessionExpiry = Date.now() + 5 * 60 * 1000;
    localStorage.setItem("session_expiry", sessionExpiry);
  } else {
    sessionExpiry = parseInt(sessionExpiry, 10);
  }

  function updateTimer() {
    const now = Date.now();
    const remaining = Math.max(0, Math.round((sessionExpiry - now) / 1000));
    
    if (remaining > 0) {
      const minutes = Math.floor(remaining / 60);
      const seconds = remaining % 60;
      const formatted = String(minutes).padStart(2, '0') + ":" + String(seconds).padStart(2, '0');
      timerEl.textContent = formatted;
      
      // Timer styling warning
      if (remaining <= 30) {
        timerEl.className = "badge error animate-pulse";
      } else if (remaining <= 60) {
        timerEl.className = "badge warning";
      } else {
        timerEl.className = "badge success";
      }
    } else {
      timerEl.textContent = "Time's Up!";
      timerEl.className = "badge error";
      
      // Disable message input
      inputEl.disabled = true;
      inputEl.placeholder = "Session expired. Please log in again.";
      fileEl.disabled = true;
      sendBtn.disabled = true;
      
      clearInterval(timerInterval);
    }
  }
  const timerInterval = setInterval(updateTimer, 1000);
  updateTimer();

  // Helper: Markdown parser
  function renderMarkdown(text) {
    if (typeof marked !== "undefined" && marked.parse) {
      try {
        return marked.parse(text);
      } catch (e) {
        console.error("Markdown parse error:", e);
        return text;
      }
    }
    return text;
  }

  // Create UI Bubbles
  function makeBubble(role, text) {
    const wrap = document.createElement("div");
    wrap.style.padding = "0.75rem 1rem";
    wrap.style.borderRadius = "0.75rem";
    wrap.style.maxWidth = "85%";
    wrap.style.whiteSpace = "pre-wrap";
    wrap.style.wordBreak = "break-word";
    
    if (role === "user") {
      wrap.style.background = "var(--accent)";
      wrap.style.alignSelf = "flex-end";
      wrap.style.color = "#fff";
      wrap.textContent = text;
    }
    return wrap;
  }

  function makeStreamingBubble() {
    const wrap = document.createElement("div");
    wrap.style.padding = "0.75rem 1rem";
    wrap.style.borderRadius = "0.75rem";
    wrap.style.maxWidth = "92%";
    wrap.style.alignSelf = "flex-start";
    wrap.style.background = "#0b1220";
    wrap.style.border = "1px solid var(--border)";
    wrap.style.display = "flex";
    wrap.style.flexDirection = "column";
    wrap.style.gap = "0.75rem";

    // Active status line (shown at top while streaming)
    const statusLine = document.createElement("div");
    statusLine.className = "text-xs font-mono text-indigo-400 flex items-center gap-1.5";
    statusLine.innerHTML = `<span class="spinner"></span> <span>Running orchestrator...</span>`;
    wrap.appendChild(statusLine);

    // \u2500\u2500 Chatbot markdown text (FIRST \u2014 shown above products) \u2500\u2500
    const textEl = document.createElement("div");
    textEl.className = "markdown-body";
    textEl.textContent = "\u231b Initiating assistant...";
    wrap.appendChild(textEl);

    // \u2500\u2500 Divider (only visible when products are also shown) \u2500\u2500
    const divider = document.createElement("hr");
    divider.style.cssText = "border:none;border-top:1px solid #1e293b;display:none;";
    wrap.appendChild(divider);

    // \u2500\u2500 Product Cards Section (shown BELOW text when db_res arrives) \u2500\u2500
    const productsSection = document.createElement("div");
    // NOTE: do NOT use Tailwind 'hidden' class here \u2014 it sets display:none !important
    // which cannot be overridden by inline style later. Use pure inline style instead.
    productsSection.style.display = "none";

    const productsLabel = document.createElement("div");
    productsLabel.style.cssText = "display:flex;align-items:center;gap:0.5rem;margin-bottom:0.75rem;";
    const countBadgeEl = document.createElement("span");
    countBadgeEl.className = "prod-count-badge";
    countBadgeEl.style.cssText = "font-size:0.65rem;background:rgba(99,102,241,0.15);border:1px solid rgba(99,102,241,0.3);color:#a5b4fc;border-radius:999px;padding:0.1rem 0.5rem;";
    productsLabel.innerHTML = `
      <span style="display:inline-flex;align-items:center;gap:0.35rem;font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.07em;color:#818cf8;">
        <svg xmlns='http://www.w3.org/2000/svg' width='14' height='14' fill='none' viewBox='0 0 24 24' stroke='currentColor' stroke-width='2.5'><path stroke-linecap='round' stroke-linejoin='round' d='M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z'/></svg>
        Recommended Products
      </span>
    `;
    productsLabel.appendChild(countBadgeEl);
    wrap.countBadgeEl = countBadgeEl;
    productsSection.appendChild(productsLabel);

    const productsGrid = document.createElement("div");
    productsGrid.className = "product-grid";
    productsSection.appendChild(productsGrid);

    wrap.appendChild(productsSection);


    // ── Technical Logs (collapsed by default, at the bottom) ──
    const details = document.createElement("details");
    details.className = "mt-1 text-xs text-slate-400 border border-slate-700 rounded bg-slate-950/50";

    const summary = document.createElement("summary");
    summary.className = "cursor-pointer select-none text-slate-300 hover:text-white font-semibold p-2 outline-none";
    summary.textContent = "Technical Logs / Execution Steps";
    details.appendChild(summary);

    const logsList = document.createElement("div");
    logsList.className = "logs-list space-y-1.5 p-2 border-t border-slate-800 font-mono text-[11px] overflow-x-auto max-h-40";
    details.appendChild(logsList);
    wrap.appendChild(details);

    wrap.textEl = textEl;
    wrap.statusLine = statusLine;
    wrap.logsList = logsList;
    wrap.productsGrid = productsGrid;
    wrap.productsSection = productsSection;
    wrap.divider = divider;

    return wrap;
  }

  function appendNode(node) {
    if (emptyEl && emptyEl.parentNode) emptyEl.parentNode.removeChild(emptyEl);
    logEl.appendChild(node);
    logEl.scrollTop = logEl.scrollHeight;
  }

  // ── Upload trigger ──
  uploadTrigger.addEventListener("click", function () {
    fileEl.click();
  });

  // ── File picker → show image preview ──
  function showPreview(file) {
    if (!file) return;
    const url = URL.createObjectURL(file);
    imgPreviewThumb.src = url;
    imgPreviewName.textContent = file.name;
    imgPreviewWrap.style.display = "flex";
  }

  function clearPreview() {
    if (imgPreviewThumb.src && imgPreviewThumb.src.startsWith("blob:")) {
      URL.revokeObjectURL(imgPreviewThumb.src);
    }
    imgPreviewThumb.src = "";
    imgPreviewName.textContent = "";
    imgPreviewWrap.style.display = "none";
    fileEl.value = "";
  }

  fileEl.addEventListener("change", function () {
    if (fileEl.files && fileEl.files[0]) {
      showPreview(fileEl.files[0]);
    } else {
      clearPreview();
    }
  });

  imgRemoveBtn.addEventListener("click", function () {
    clearPreview();
  });

  // ── Enter to send, Shift+Enter for newline ──
  inputEl.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!sendBtn.disabled) formEl.requestSubmit();
    }
  });

  formEl.addEventListener("submit", function (e) {
    e.preventDefault();
    const message = inputEl.value.trim();
    if (!message) return;
    const file = fileEl.files && fileEl.files[0] ? fileEl.files[0] : null;

    // Build user bubble — show image thumbnail inline if attached
    const userWrap = document.createElement("div");
    userWrap.style.cssText = "display:flex;flex-direction:column;align-items:flex-end;gap:0.35rem;";

    if (file) {
      const thumbUrl = imgPreviewThumb.src;
      const thumbImg = document.createElement("img");
      thumbImg.src = thumbUrl;
      thumbImg.alt = file.name;
      thumbImg.style.cssText = "width:120px;height:120px;object-fit:cover;border-radius:0.5rem;border:1px solid var(--border);align-self:flex-end;";
      userWrap.appendChild(thumbImg);
    }

    const textBubble = document.createElement("div");
    textBubble.style.cssText = "padding:0.6rem 1rem;border-radius:0.75rem;max-width:85%;word-break:break-word;background:var(--accent);color:#fff;align-self:flex-end;white-space:pre-wrap;";
    textBubble.textContent = message;
    userWrap.appendChild(textBubble);
    appendNode(userWrap);

    inputEl.value = "";
    clearPreview();

    const bubble = makeStreamingBubble();
    appendNode(bubble);

    sendBtn.disabled = true;
    
    window.api.streamChat({
      body: { message: message, thread_id: threadLabel.textContent || "" },
      file: file,
      onChunk: function (line) {
        if (!line.startsWith("data:")) return;
        const jsonStr = line.replace(/^data:\s*/, "").trim();
        if (!jsonStr) return;
        
        let chunk;
        try {
          chunk = JSON.parse(jsonStr);
        } catch (e) {
          console.error("JSON parse error:", e);
          return;
        }

        // 1. Log chunk in Technical Details
        const logItem = document.createElement("div");
        logItem.style.borderBottom = "1px dashed #334155";
        logItem.style.paddingBottom = "0.3rem";
        
        const timestamp = new Date().toLocaleTimeString();
        logItem.innerHTML = `<strong class="text-indigo-300">[${timestamp}]</strong> <pre class="mt-1 text-slate-300 whitespace-pre-wrap text-[10px] bg-slate-900/60 p-1.5 rounded">${JSON.stringify(chunk, null, 2)}</pre>`;
        bubble.logsList.appendChild(logItem);

        // 2. Process Orchestrator Update
        if (chunk.orchestrator) {
          const redirect = chunk.orchestrator.redirect_to;
          const query = chunk.orchestrator.query_for_db_search;
          if (redirect === "retreiver_node") {
            bubble.statusLine.innerHTML = `<span class="spinner"></span> <span>Retrieving from database for query: "${query}"...</span>`;
          } else {
            bubble.statusLine.innerHTML = `<span class="spinner"></span> <span>Generating direct response...</span>`;
          }
        }

        // 3. Process Retriever Node Update (db_res)
        // NOTE: LangGraph registers the node as "retreiver" (see builder.py line 18:
        //   workflow.add_node("retreiver", retreiver_node))
        // stream_mode="updates" yields chunks keyed by the registered node name.
        // So the correct key is chunk.retreiver, NOT chunk.retreiver_node.
        if (chunk.retreiver) {
          const dbRes = chunk.retreiver.db_res || [];
          if (dbRes.length > 0) {
            bubble.statusLine.innerHTML = `<span class="spinner"></span> <span>Found ${dbRes.length} matching products. Generating response...</span>`;

            // Update count badge (use the direct reference stored on wrap)
            if (bubble.countBadgeEl) bubble.countBadgeEl.textContent = `${dbRes.length} results`;

            // Build Product cards
            bubble.productsGrid.innerHTML = "";
            dbRes.forEach((item) => {
              const meta = item.metadata || {};
              const score = item.score ? Math.round(item.score * 100) : null;
              const discounted = Number(meta.discounted_price || meta.price || 0);
              const original   = Number(meta.price || 0);
              const savings    = original > discounted ? original - discounted : 0;
              const discountPct = original > discounted
                ? Math.round(((original - discounted) / original) * 100)
                : 0;

              const card = document.createElement("div");
              card.className = "product-card";

              // ── Discount badge top-left ──
              if (discountPct > 0) {
                const discBadge = document.createElement("span");
                discBadge.className = "product-discount-badge";
                discBadge.textContent = `-${discountPct}%`;
                card.appendChild(discBadge);
              }

              // ── Match score badge top-right ──
              if (score !== null) {
                const scoreBadge = document.createElement("span");
                scoreBadge.className = "product-score-badge";
                scoreBadge.textContent = `${score}% match`;
                card.appendChild(scoreBadge);
              }

              // ── Image ──
              const imgWrapper = document.createElement("div");
              imgWrapper.className = "product-img-wrapper";

              const img = document.createElement("img");
              img.className = "product-img";
              img.src = meta.image_url || "";
              img.alt = meta.name || "Product";
              img.loading = "lazy";
              img.onerror = () => { img.src = "https://placehold.co/300x300/f8fafc/6366f1?text=No+Image"; };
              imgWrapper.appendChild(img);
              card.appendChild(imgWrapper);

              // ── Info section ──
              const info = document.createElement("div");
              info.className = "product-info";

              // Brand
              const brand = document.createElement("span");
              brand.className = "product-brand";
              brand.textContent = meta.brand || "";
              info.appendChild(brand);

              // Title
              const title = document.createElement("h4");
              title.className = "product-title";
              title.title = meta.name || "";
              title.textContent = meta.name || "Product";
              info.appendChild(title);

              // Usage tag
              if (meta.usage) {
                const usageTag = document.createElement("span");
                usageTag.className = "product-usage-tag";
                usageTag.textContent = meta.usage;
                info.appendChild(usageTag);
              }

              // Price row
              const priceRow = document.createElement("div");
              priceRow.className = "product-price-row";

              if (discounted) {
                const priceEl = document.createElement("span");
                priceEl.className = "product-price";
                priceEl.textContent = `₹${discounted.toLocaleString("en-IN")}`;
                priceRow.appendChild(priceEl);
              }

              if (savings > 0) {
                const mrpEl = document.createElement("span");
                mrpEl.className = "product-old-price";
                mrpEl.textContent = `₹${original.toLocaleString("en-IN")}`;
                priceRow.appendChild(mrpEl);

                const saveEl = document.createElement("span");
                saveEl.className = "product-saving";
                saveEl.textContent = `Save ₹${savings.toLocaleString("en-IN")}`;
                priceRow.appendChild(saveEl);
              }
              info.appendChild(priceRow);

              // CTA button
              if (meta.image_url) {
                const link = document.createElement("a");
                link.className = "product-link";
                link.href = meta.image_url;
                link.target = "_blank";
                link.rel = "noopener noreferrer";
                link.textContent = "View Product";
                info.appendChild(link);
              }

              card.appendChild(info);
              bubble.productsGrid.appendChild(card);
            });


            // Reveal the products section (pure inline style — no Tailwind class conflict)
            bubble.productsSection.style.display = "block";
            bubble.divider.style.display = "block";
            logEl.scrollTop = logEl.scrollHeight;
          } else {
            bubble.statusLine.innerHTML = `<span class="spinner"></span> <span>No products found. Chatting directly...</span>`;
          }
        }

        // 4. Process Chat Output (Text content streaming typing effect)
        if (chunk.chat) {
          bubble.statusLine.innerHTML = `<span class="spinner"></span> <span>Formatting response...</span>`;
          
          let rawText = "";
          const messages = chunk.chat.messages || [];
          const lastMsg = messages[messages.length - 1];
          if (lastMsg) {
            if (typeof lastMsg === 'string') {
              rawText = lastMsg;
            } else if (lastMsg.content) {
              rawText = lastMsg.content;
            } else if (lastMsg.kwargs && lastMsg.kwargs.content) {
              rawText = lastMsg.kwargs.content;
            }
          }
          
          if (rawText) {
            if (bubble.typingInterval) clearInterval(bubble.typingInterval);
            
            bubble.textEl.textContent = "";
            let index = 0;
            let currentText = "";
            bubble.typingInterval = setInterval(() => {
              if (index < rawText.length) {
                const step = 4;
                currentText += rawText.slice(index, index + step);
                index += step;
                bubble.textEl.innerHTML = renderMarkdown(currentText);
                logEl.scrollTop = logEl.scrollHeight;
              } else {
                clearInterval(bubble.typingInterval);
                bubble.textEl.innerHTML = renderMarkdown(rawText);
                bubble.statusLine.innerHTML = `✅ Complete.`;
                logEl.scrollTop = logEl.scrollHeight;
              }
            }, 15);
          } else {
            bubble.textEl.textContent = "No text response generated.";
            bubble.statusLine.innerHTML = `✅ Complete.`;
          }
        }
      },
      onDone: function () {
        sendBtn.disabled = false;
      },
      onError: function (err) {
        sendBtn.disabled = false;
        bubble.textEl.textContent = "Error: " + (err && err.message ? err.message : String(err));
        bubble.statusLine.innerHTML = `<span class="text-red-500 font-bold">❌ Error occurred.</span>`;
      },
    });
  });

  logoutBtn.addEventListener("click", function () {
    document.cookie = "thread_id=; Max-Age=0; path=/";
    localStorage.removeItem("session_expiry");
    localStorage.removeItem("session_duration_minutes");
    window.location.replace(window.PAGES.LOGIN);
  });
})();
