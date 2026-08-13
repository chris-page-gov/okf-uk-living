"use strict";

(() => {
  const PROJECTION_SHA256 = "@@PROJECTION_SHA256@@";
  const template = document.getElementById("projection-data");
  if (!(template instanceof HTMLTemplateElement)) {
    throw new Error("Embedded journey projection is missing");
  }
  const projection = JSON.parse(template.content.textContent || "{}");
  const families = Array.isArray(projection.families) ? projection.families : [];
  const familyById = new Map(families.map((family) => [String(family.id), family]));
  const nations = ["All UK", "England", "Scotland", "Wales", "Northern Ireland"];
  const jurisdictionMembers = Object.freeze({
    "England": ["England"],
    "England and Wales": ["England", "Wales"],
    "England, Scotland and Wales": ["England", "Scotland", "Wales"],
    "Great Britain": ["England", "Scotland", "Wales"],
    "Northern Ireland": ["Northern Ireland"],
    "Scotland": ["Scotland"],
    "Wales": ["Wales"]
  });
  const state = {
    query: "",
    nation: "All UK",
    selectedId: ""
  };

  const byId = (id) => {
    const node = document.getElementById(id);
    if (!node) throw new Error(`Missing interface element: ${id}`);
    return node;
  };

  const empty = (node) => {
    while (node.firstChild) node.removeChild(node.firstChild);
  };

  const text = (tag, value, className = "") => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    node.textContent = String(value ?? "");
    return node;
  };

  const appendList = (node, values) => {
    empty(node);
    for (const value of Array.isArray(values) ? values : []) {
      node.append(text("li", value));
    }
  };

  const normalise = (value) => String(value || "")
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLocaleLowerCase("en-GB")
    .replace(/[^a-z0-9]+/g, " ")
    .trim();

  const safeHttpsUrl = (value) => {
    const raw = String(value || "");
    if (!raw || /[\s\u0000-\u001f\u007f"'<>\\^`{|}]/.test(raw) || /%(?![0-9a-f]{2})/i.test(raw)) return null;
    try {
      const url = new URL(raw);
      if (url.protocol !== "https:" || url.username || url.password || !url.hostname) return null;
      if (url.port && Number(url.port) === 0) return null;
      return url;
    } catch (_error) {
      return null;
    }
  };

  const externalLink = (url, label) => {
    const safe = safeHttpsUrl(url);
    if (!safe) return text("span", `${label} — unsafe link withheld`);
    const link = document.createElement("a");
    link.href = safe.href;
    link.target = "_blank";
    link.rel = "noopener noreferrer external";
    link.referrerPolicy = "no-referrer";
    link.textContent = `${label} (opens in a new tab)`;
    return link;
  };

  const renderFactValue = (value) => {
    const detail = document.createElement("dd");
    if (value && typeof value === "object" && !Array.isArray(value)) {
      const stateLabel = String(value.state || "not stated").replace(/_/g, " ");
      detail.append(text("span", `State: ${stateLabel}`, "fact-state"));
      if (typeof value.summary === "string") {
        detail.append(text("span", `Summary: ${value.summary}`, "fact-narrative"));
      } else if (typeof value.reason === "string") {
        detail.append(text("span", `Reason: ${value.reason}`, "fact-narrative"));
      } else {
        detail.append(text("span", "Narrative: not stated", "fact-narrative"));
      }
      return detail;
    }
    detail.append(text("span", `State: not stated`, "fact-state"));
    detail.append(text("span", `Narrative: ${String(value || "not stated")}`, "fact-narrative"));
    return detail;
  };

  const familySearchText = (family) => normalise([
    family.id,
    family.title,
    family.description,
    family.domain?.title,
    family.process?.title,
    ...(family.aliases || []),
    ...(family.situations || []),
    ...(family.user_needs || []),
    ...(family.search_text || [])
  ].join(" "));

  const searchIndex = new Map(families.map((family) => [family.id, familySearchText(family)]));

  const matchingFamilies = () => {
    const tokens = normalise(state.query).split(" ").filter(Boolean);
    const ranked = families.map((family) => {
      const haystack = searchIndex.get(family.id) || "";
      const title = normalise(family.title);
      const aliases = normalise((family.aliases || []).join(" "));
      if (!tokens.every((token) => haystack.includes(token))) return null;
      let score = 0;
      for (const token of tokens) {
        if (title.includes(token)) score += 4;
        if (aliases.includes(token)) score += 6;
        score += 1;
      }
      return { family, score };
    }).filter(Boolean);
    ranked.sort((left, right) => right.score - left.score || left.family.title.localeCompare(right.family.title, "en-GB"));
    return ranked.map((item) => item.family);
  };

  const setHash = (familyId) => {
    const encoded = encodeURIComponent(familyId);
    if (location.hash.slice(1) !== encoded) history.replaceState(null, "", `#${encoded}`);
  };

  const clearFamilySelection = () => {
    state.selectedId = "";
    if (location.hash) history.replaceState(null, "", `${location.pathname}${location.search}`);
    byId("journey-empty").hidden = false;
    byId("journey-view").hidden = true;
  };

  const selectFamily = (familyId, focusTitle = false) => {
    if (!familyById.has(familyId)) return;
    state.selectedId = familyId;
    setHash(familyId);
    renderResults();
    renderFamily(familyById.get(familyId));
    if (focusTitle) byId("journey-title").focus({ preventScroll: false });
  };

  const renderNationOptions = () => {
    const container = byId("nation-options");
    for (const [index, nation] of nations.entries()) {
      const wrapper = document.createElement("div");
      wrapper.className = "nation-choice";
      const input = document.createElement("input");
      input.type = "radio";
      input.name = "route-nation";
      input.id = `route-nation-${index}`;
      input.value = nation;
      input.checked = nation === state.nation;
      const label = document.createElement("label");
      label.htmlFor = input.id;
      label.textContent = nation;
      input.addEventListener("change", () => {
        if (!input.checked) return;
        state.nation = nation;
        const family = familyById.get(state.selectedId);
        if (family) renderFamily(family);
      });
      wrapper.append(input, label);
      container.append(wrapper);
    }
  };

  const renderResults = (matches = matchingFamilies()) => {
    const container = byId("family-results");
    empty(container);
    const cap = 80;
    byId("result-count").textContent = matches.length > cap
      ? `${matches.length} matching families. Showing the first ${cap}.`
      : `${matches.length} matching ${matches.length === 1 ? "family" : "families"}.`;
    for (const family of matches.slice(0, cap)) {
      const listItem = document.createElement("li");
      const button = document.createElement("button");
      button.type = "button";
      button.className = "family-result";
      button.setAttribute("aria-current", String(family.id === state.selectedId));
      button.append(
        text("strong", family.title),
        text("small", family.process?.title || family.domain?.title || "Service family")
      );
      button.addEventListener("click", () => selectFamily(family.id, true));
      listItem.append(button);
      container.append(listItem);
    }
  };

  const badge = (label, className = "") => text("span", label, `badge ${className}`.trim());

  const renderBadges = (family) => {
    const container = byId("journey-badges");
    empty(container);
    container.append(badge(family.domain?.title || "Unknown domain"));
    const status = String(family.review?.specialist_review || "required");
    const statusClass = status === "not_required" ? "review-not-required" : "review-required";
    const reviewLabel = status === "not_required" ? "Specialist review not required" : "Specialist review required";
    container.append(badge(reviewLabel, statusClass));
    const assertionStatus = String(family.assertion_status || "normalised");
    const assertionLabel = assertionStatus === "normalized"
      ? "normalised"
      : assertionStatus.replaceAll("_", " ");
    container.append(badge(`Assertion: ${assertionLabel}`));
  };

  const sourceById = (family) => new Map((family.sources || []).map((source) => [String(source.id), source]));

  const routeIncludesNation = (jurisdiction, nation) => (
    nation !== "All UK"
    && (jurisdictionMembers[String(jurisdiction)] || []).includes(nation)
  );

  const renderRoutes = (family) => {
    const container = byId("official-routes");
    empty(container);
    const chosen = state.nation;
    const rows = Array.isArray(family.applicability) ? family.applicability : [];
    byId("route-note").textContent = chosen === "All UK"
      ? "All authored jurisdiction routes are shown."
      : `Routes explicitly applicable to ${chosen} are emphasised.`;
    const resources = sourceById(family);
    for (const item of rows) {
      const card = document.createElement("article");
      card.className = `route-card${routeIncludesNation(item.jurisdiction, chosen) ? " selected" : ""}`;
      const heading = document.createElement("h4");
      heading.append(text("span", item.jurisdiction), text("span", item.state || "source-defined", "route-state"));
      card.append(heading);
      const variants = Array.isArray(item.route_variants) ? item.route_variants : [];
      if (variants.length) {
        card.append(text("p", variants.map((variant) => variant.label || variant.id).join(" · ")));
      }
      const list = document.createElement("ul");
      list.className = "source-list";
      const primaryIds = new Set(variants.map((variant) => String(variant.primary_source || "")));
      for (const sourceId of item.source_ids || item.sources || []) {
        const resource = resources.get(String(sourceId));
        if (!resource) continue;
        const li = document.createElement("li");
        li.append(externalLink(resource.url, resource.title || resource.name || sourceId));
        if (primaryIds.has(String(sourceId))) li.append(text("span", "Primary route", "primary-source"));
        li.append(text("small", `${resource.owner || "Source owner not stated"} · observed ${resource.observed_at || "date not stated"}`));
        const sourceDetails = document.createElement("details");
        sourceDetails.className = "source-provenance";
        const sourceSummary = document.createElement("summary");
        sourceSummary.textContent = "Source provenance";
        const sourceFacts = document.createElement("dl");
        provenanceRow(sourceFacts, "Authority role", resource.authority_role || "Not stated");
        provenanceRow(sourceFacts, "Jurisdiction basis", resource.jurisdiction_basis || "Not stated");
        provenanceRow(sourceFacts, "Freshness", resource.freshness || "Not stated");
        provenanceRow(sourceFacts, "Rights", resource.rights_decision || "Not stated");
        provenanceRow(sourceFacts, "Limitations", (resource.limitations || []).join(" ") || "Not stated");
        sourceDetails.append(sourceSummary, sourceFacts);
        li.append(sourceDetails);
        list.append(li);
      }
      if (!list.childElementCount) list.append(text("li", "No official source is asserted for this route."));
      card.append(list);
      container.append(card);
    }
  };

  const factLabels = [
    ["requirements", "Requirements"],
    ["evidence", "Evidence"],
    ["rule", "Rule"],
    ["channel", "Channel"],
    ["cost", "Cost"],
    ["time", "Time"],
    ["output", "Output"],
    ["outcome", "Outcome"],
    ["redress", "Redress"]
  ];

  const renderStep = (step) => {
    const item = document.createElement("li");
    item.className = "step";
    item.append(text("h5", step.interaction || step.title || step.id));
    item.append(text("p", `Provider: ${step.provider || "not stated"}`, "provider"));
    const facts = document.createElement("dl");
    facts.className = "step-facts";
    for (const [key, label] of factLabels) {
      if (!(key in step)) continue;
      const pair = document.createElement("div");
      pair.append(text("dt", label), renderFactValue(step[key]));
      facts.append(pair);
    }
    item.append(facts);
    const assertions = step.relationship_assertions || {};
    const assertionIds = [
      assertions.episode_step,
      assertions.follows_previous,
      assertions.precedes_next,
      ...(Array.isArray(assertions.sources) ? assertions.sources.map((source) => source.assertion_id) : [])
    ].filter(Boolean);
    if (assertionIds.length) item.append(text("p", `Governed assertions: ${assertionIds.join(" · ")}`, "assertion-line"));
    return item;
  };

  const renderEpisodes = (family) => {
    const container = byId("journey-episodes");
    empty(container);
    const episodes = [...(family.episodes || [])].sort((left, right) => {
      const kind = (value) => value.kind === "ordinary" ? 0 : 1;
      return kind(left) - kind(right) || Number(left.order || 0) - Number(right.order || 0);
    });
    for (const episode of episodes) {
      const section = document.createElement("section");
      section.className = `episode ${episode.kind === "ordinary" ? "ordinary" : "exception"}`;
      const header = document.createElement("header");
      header.className = "episode-header";
      header.append(text("span", episode.kind === "ordinary" ? "Ordinary" : "Exception", "episode-kind"));
      const copy = document.createElement("div");
      copy.append(text("h4", episode.title || episode.id));
      copy.append(text("p", `Entry: ${episode.entry_state || "not stated"}`));
      copy.append(text("p", `Outcome: ${episode.outcome || "not stated"}`));
      header.append(copy);
      section.append(header);
      const list = document.createElement("ol");
      list.className = "step-list";
      const steps = [...(episode.steps || [])].sort((left, right) => Number(left.order || 0) - Number(right.order || 0));
      for (const step of steps) list.append(renderStep(step));
      section.append(list);
      container.append(section);
    }
  };

  const renderRelated = (family) => {
    const container = byId("related-families");
    empty(container);
    const related = Array.isArray(family.related_families) ? family.related_families : [];
    byId("related-section").hidden = related.length === 0;
    for (const item of related) {
      const relatedFamily = familyById.get(String(item.id));
      if (!relatedFamily) continue;
      const listItem = document.createElement("li");
      const button = document.createElement("button");
      button.type = "button";
      button.className = "related-button";
      button.textContent = relatedFamily.title;
      button.addEventListener("click", () => selectFamily(relatedFamily.id, true));
      listItem.append(button);
      container.append(listItem);
    }
  };

  const provenanceRow = (list, label, value) => {
    list.append(text("dt", label), text("dd", value));
  };

  const renderProvenance = (family) => {
    const list = byId("provenance-list");
    empty(list);
    const source = projection.source_identity || {};
    provenanceRow(list, "Family route", family.route || `dataset/${family.id}`);
    provenanceRow(list, "Family IRI", `https://chris-page-gov.github.io/okf-uk-living/id/${family.route}`);
    provenanceRow(list, "Authored source", family.narrative?.source || "Not stated");
    provenanceRow(list, "Snapshot", projection.snapshot || "Not stated");
    provenanceRow(list, "Candidate", source.candidate_id || "Not stated");
    provenanceRow(list, "Source snapshots retained", "0");
    provenanceRow(list, "Base descriptor SHA-256", source.bundle_descriptor?.sha256 || "Not stated");
    provenanceRow(list, "Relationship runtime SHA-256", source.relationship_runtime?.sha256 || "Not stated");
    provenanceRow(list, "Projection SHA-256", PROJECTION_SHA256);
    provenanceRow(list, "Family→domain assertion", family.relationship_assertions?.life_course_domain || "Not stated");
    provenanceRow(list, "Family→process assertion", family.relationship_assertions?.enclosing_process || "Not stated");
    provenanceRow(list, "List-fragment projection rule", projection.normalisation?.comma_fragments || "Not stated");
    provenanceRow(list, "Step-fact projection rule", projection.normalisation?.step_fact_flow_mapping_fragments || "Not stated");
  };

  const renderFamily = (family) => {
    byId("journey-empty").hidden = true;
    byId("journey-view").hidden = false;
    byId("journey-context").textContent = `${family.domain?.title || "Unknown domain"} · ${family.process?.title || "Unassigned process"}`;
    byId("journey-title").textContent = family.title;
    byId("journey-description").textContent = family.description || "";
    byId("interaction-boundary").textContent = family.interaction_boundary || "Consult the cited official source before acting.";
    appendList(byId("limitations"), family.limitations || []);
    appendList(byId("situations"), family.situations || []);
    appendList(byId("user-needs"), family.user_needs || []);
    renderBadges(family);
    renderRoutes(family);
    renderEpisodes(family);
    renderRelated(family);
    renderProvenance(family);
  };

  byId("family-total").textContent = String(projection.counts?.families ?? families.length);
  byId("projection-digest").textContent = PROJECTION_SHA256;
  const counts = projection.counts || {};
  byId("review-summary").textContent = `${counts.specialist_review_accepted ?? 0} accepted · ${counts.specialist_review_not_required ?? 0} not required · ${counts.specialist_review_required ?? 0} required`;
  renderNationOptions();
  const input = byId("journey-search");
  input.addEventListener("input", () => {
    state.query = input.value;
    const matches = matchingFamilies();
    if (state.selectedId && !matches.some((family) => family.id === state.selectedId)) {
      clearFamilySelection();
    }
    renderResults(matches);
  });
  renderResults();

  let initialId = "";
  try {
    initialId = decodeURIComponent(location.hash.slice(1));
  } catch (_error) {
    initialId = "";
  }
  if (!familyById.has(initialId)) {
    initialId = familyById.has("report-missed-rubbish-collection")
      ? "report-missed-rubbish-collection"
      : String(families[0]?.id || "");
  }
  if (initialId) selectFamily(initialId, false);
})();
