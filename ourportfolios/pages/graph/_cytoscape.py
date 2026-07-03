"""Cytoscape.js JavaScript engine embedded as a Python string for rx.script.

Now reads pre-formatted elements from the server response
(``graphData.elements``), eliminating client-side ``_formatElements()``
and hardcoded style constants.
"""

_CYTOSCAPE_JS = """
// ── Cytoscape.js Graph Engine ──────────────────────────────────────────────
window._cy = null;
window._fullElements = [];

// ── Style builder (reads from server-supplied window._graphData.style) ────
function _buildCyStyle() {
    var styleData = (window._graphData && window._graphData.style) || {};
    const nodeColors = styleData.nodeColors || window._nodeColors || {};
    const nodeShapes = styleData.nodeShapes || window._nodeShapes || {};
    const companyTypeColors = styleData.companyTypeColors || window._companyTypeColors || {};
    const relColors = styleData.relColors || window._relColors || {};
    const relStyles = styleData.relStyles || window._relStyles || {};

    const nodeStyles = Object.entries(nodeColors).map(function(entry) {
        var ntype = entry[0];
        var color = entry[1];
        return {
            selector: 'node[ntype="' + ntype + '"]',
            style: {
                'background-color': color,
                'shape': nodeShapes[ntype] || 'ellipse',
                'label': 'data(label)',
                'font-size': ntype === 'Company' ? '15px' : (ntype === 'Industry' ? '13px' : '11px'),
                'color': '#ffffff',
                'text-outline-color': '#0f172a',
                'text-outline-width': 2,
                'text-background-color': 'rgba(0,0,0,0.6)',
                'text-background-opacity': 0.7,
                'text-background-shape': 'roundrectangle',
                'text-background-padding': '2px',
                'text-valign': 'bottom',
                'text-halign': 'center',
                'text-margin-y': 6,
            }
        };
    });

    Object.entries(companyTypeColors).forEach(function(entry) {
        var ctype = entry[0];
        var color = entry[1];
        nodeStyles.push({
            selector: 'node[ntype="Company"][company_type="' + ctype + '"]',
            style: { 'background-color': color }
        });
    });

    // Industry nodes — use a muted version of their color
    nodeStyles.push({
        selector: 'node[ntype="Industry"]',
        style: { 'background-color': '#f59e0b', 'border-width': 3, 'border-color': '#d97706' }
    });
    nodeStyles.push({
        selector: 'node[ntype="Industry"]',
        style: {
            'text-valign': 'center',
            'text-halign': 'center',
            'text-margin-y': 0,
        }
    });

    var edgeStyles = Object.entries(relColors).map(function(entry) {
        var rtype = entry[0];
        var color = entry[1];
        var lstyle = relStyles[rtype] || 'solid';
        var arrowShape = rtype === 'HOLDS_STAKE_IN' || rtype === 'SUBSIDIARY_OF' ? 'diamond'
            : rtype === 'COMPETES_WITH' ? 'tee'
            : rtype === 'IS_OFFICER' || rtype === 'IS_BOARD_MEMBER' || rtype === 'IS_FOUNDER' || rtype === 'IS_EXECUTIVE' ? 'triangle'
            : rtype === 'BELONGS_TO_INDUSTRY' ? 'none'
            : rtype === 'AFFECTS_SECTOR' || rtype === 'AFFECTS_INDUSTRY' || rtype === 'HAS_MACRO_INDICATOR' ? 'circle'
            : 'triangle';
        var edgeWidth = rtype === 'HOLDS_STAKE_IN' || rtype === 'SUBSIDIARY_OF' ? 2.5
            : rtype === 'COMPETES_WITH' ? 2
            : 1.5;
        var edgeOpacity = rtype === 'BELONGS_TO_INDUSTRY' ? 0.5
            : rtype === 'AFFECTS_SECTOR' || rtype === 'AFFECTS_INDUSTRY' || rtype === 'HAS_MACRO_INDICATOR' ? 0.6
            : 0.8;
        return {
            selector: 'edge[rtype="' + rtype + '"]',
            style: {
                'line-color': color,
                'target-arrow-color': color,
                'target-arrow-shape': arrowShape,
                'line-style': lstyle,
                'width': edgeWidth,
                'line-opacity': edgeOpacity,
                'curve-style': (rtype === 'HOLDS_STAKE_IN' || rtype === 'SUBSIDIARY_OF') ? 'bezier' : 'haystack',
                'label': 'data(label)',
                'font-size': '8px',
                'color': 'rgba(255,255,255,0.5)',
                'text-outline-color': '#0f172a',
                'text-outline-width': 1,
                'text-background-color': 'rgba(0,0,0,0.5)',
                'text-background-opacity': 0.6,
                'text-background-shape': 'roundrectangle',
                'text-background-padding': '1px',
                'edge-text-rotation': 'autorotate',
            }
        };
    });

    return []
        .concat(nodeStyles)
        .concat(edgeStyles)
        .concat([
            {
                selector: 'node',
                style: {
                    'width': 'mapData(size, 0, 100, 32, 65)',
                    'height': 'mapData(size, 0, 100, 32, 65)',
                    'border-width': 2,
                    'border-color': '#334155',
                    'transition-property': 'background-color, border-color, border-width',
                    'transition-duration': '0.2s',
                }
            },
            {
                selector: 'edge',
                style: {
                    'width': 2,
                    'line-color': '#475569',
                    'target-arrow-color': '#475569',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier',
                }
            },
            {
                selector: 'node:selected',
                style: {
                    'border-color': '#ffffff',
                    'border-width': 4,
                }
            },
            {
                selector: 'node:hover',
                style: {
                    'border-color': 'rgba(255,255,255,0.6)',
                    'border-width': 3,
                }
            },
            {
                selector: 'edge:selected',
                style: {
                    'line-color': '#ffffff',
                    'target-arrow-color': '#ffffff',
                    'width': 4,
                    'line-opacity': 1.0,
                    'z-index': 10,
                    'label': 'data(label)',
                    'font-size': '9px',
                    'color': '#ffffff',
                    'text-background-opacity': 0.9,
                    'text-background-color': '#1e293b',
                }
            },
            {
                selector: 'edge:hover',
                style: {
                    'line-color': 'rgba(255,255,255,0.5)',
                    'target-arrow-color': 'rgba(255,255,255,0.5)',
                    'width': 3.5,
                    'line-opacity': 0.9,
                }
            },
            {
                selector: 'node.highlighted',
                style: {
                    'border-color': '#a78bfa',
                    'border-width': 4,
                    'shadow-color': '#a78bfa',
                    'shadow-blur': 12,
                    'shadow-opacity': 0.6,
                }
            },
        ]);
}

// ── Format elements (reads server-precomputed elements) ──
function _formatElements(graphData) {
    if (graphData && graphData.elements && graphData.elements.length > 0) {
        return graphData.elements;
    }
    return [];
}

window.initCyGraph = function(graphData) {
    _destroyCy();
    var container = document.getElementById('cy-graph');
    if (!container) return;

    // Update style globals from server response
    if (graphData && graphData.style) {
        window._nodeColors = graphData.style.nodeColors || {};
        window._nodeShapes = graphData.style.nodeShapes || {};
        window._companyTypeColors = graphData.style.companyTypeColors || {};
        window._relColors = graphData.style.relColors || {};
        window._relStyles = graphData.style.relStyles || {};
        if (graphData.style.categoryMap) {
            window._categoryMap = graphData.style.categoryMap;
        }
    }

    window._fullElements = _formatElements(graphData);

    if (!window._fullElements || window._fullElements.length === 0) {
        console.warn('[cy] No elements to render — graph data may be empty');
        return;
    }

    window._cy = cytoscape({
        container: container,
        elements: window._fullElements,
        style: _buildCyStyle(),
        layout: { name: 'null' },  // Don't layout yet — filters + radial first
        minZoom: 0.08,
        maxZoom: 5,
        wheelSensitivity: 0.4,
    });

    // Apply filters, then lay out visible nodes in a deterministic radial pattern
    window._applyFilters();
    window._applyRadialLayout();
    window._cy.fit(window._cy.nodes(':visible'), 120);
    window._sendVisibleCounts();

    // ResizeObserver — Cytoscape needs to know when container resizes
    var _ro = new ResizeObserver(function() {
        if (window._cy) window._cy.resize();
    });
    _ro.observe(container);

    window._cy.on('tap', 'node', function(evt) {
        var node = evt.target;
        var nodeId = node.id();
        console.log('[cy] node tap:', nodeId);
        window._cy.nodes().unselect();
        window._cy.edges().unselect();
        node.select();
        window._showImmediateNeighbors(node);
        if (window._reflexSend) {
            console.log('[cy] calling _reflexSend for node:', nodeId);
            window._reflexSend('graph_state.handle_node_click', {node_id: nodeId});
        } else {
            console.error('[cy] _reflexSend is NOT DEFINED');
        }
    });

    window._cy.on('tap', 'edge', function(evt) {
        var edge = evt.target;
        var edgeId = edge.id();
        window._cy.nodes().unselect();
        window._cy.edges().unselect();
        edge.select();
        window._showEdgeEndpoints(edge);
        if (window._reflexSend) {
            window._reflexSend('graph_state.handle_edge_click', {edge_id: edgeId});
        }
    });

    window._cy.on('tap', function(evt) {
        if (evt.target === window._cy) {
            window._cy.nodes().unselect();
            window._cy.edges().unselect();
            window._cy.elements().show();
            window._applyFilters();
            if (window._reflexSend) {
                window._reflexSend('graph_state.handle_background_click', {});
            }
        }
    });
}

// ── Node click highlight ────────────────────────────────────────────────────
window._showImmediateNeighbors = function(node) {
    if (!window._cy) return;
    try {
        var fs = window._filterState;
        var neighborIds = {};
        neighborIds[node.id()] = true;
        node.connectedEdges().forEach(function(edge) {
            var other = edge.source().id() === node.id() ? edge.target() : edge.source();
            neighborIds[other.id()] = true;
        });

        // Nodes batch: apply node visibility first so edge .visible() sees it
        window._cy.batch(function() {
            window._cy.nodes().forEach(function(n) {
                var ntype = n.data('ntype') || '';
                if (fs.nodeType && fs.nodeType[ntype] === false) {
                    n.hide();
                    return;
                }
                var companyType = n.data('company_type') || '';
                if (ntype === 'Company' && companyType === 'subsidiary' && !fs.showSubsidiaries) {
                    n.hide();
                    return;
                }
                if (neighborIds[n.id()]) {
                    n.show();
                } else {
                    n.hide();
                }
            });
        });

        // Edges batch: now .visible() reflects the fresh node state
        window._cy.batch(function() {
            window._cy.edges().forEach(function(e) {
                var rtype = e.data('rtype') || '';
                var cat = '';
                for (var c in window._categoryMap) {
                    if (window._categoryMap[c].indexOf(rtype) >= 0) { cat = c; break; }
                }
                if (fs[cat] && e.source().visible() && e.target().visible()) {
                    e.show();
                } else {
                    e.hide();
                }
            });
        });

        var visible = window._cy.nodes(':visible');
        if (visible.length > 0) {
            window._cy.animate({
                fit: { eles: visible, padding: 50 },
                duration: 200,
                easing: 'ease-in-out-cubic',
            });
        }
    } catch(e) { console.error('[cy] _showImmediateNeighbors error:', e); }
};

// ── Edge click highlight ────────────────────────────────────────────────────
window._showEdgeEndpoints = function(edge) {
    if (!window._cy) return;
    try {
        var fs = window._filterState;
        var src = edge.source();
        var tgt = edge.target();

        // Nodes batch: apply node visibility first so edge .visible() sees it
        window._cy.batch(function() {
            window._cy.nodes().forEach(function(n) {
                var ntype = n.data('ntype') || '';
                if (fs.nodeType && fs.nodeType[ntype] === false) {
                    n.hide();
                    return;
                }
                var companyType = n.data('company_type') || '';
                if (ntype === 'Company' && companyType === 'subsidiary' && !fs.showSubsidiaries) {
                    n.hide();
                    return;
                }
                if (n.id() === src.id() || n.id() === tgt.id()) {
                    n.show();
                } else {
                    n.hide();
                }
            });
        });

        // Edges batch: now .visible() reflects the fresh node state
        window._cy.batch(function() {
            window._cy.edges().forEach(function(e) {
                var rtype = e.data('rtype') || '';
                var cat = '';
                for (var c in window._categoryMap) {
                    if (window._categoryMap[c].indexOf(rtype) >= 0) { cat = c; break; }
                }
                if (fs[cat] && e.source().visible() && e.target().visible()) {
                    e.show();
                } else {
                    e.hide();
                }
            });
        });

        var visible = window._cy.nodes(':visible');
        if (visible.length > 0) {
            window._cy.animate({
                fit: { eles: visible, padding: 50 },
                duration: 200,
                easing: 'ease-in-out-cubic',
            });
        }
    } catch(e) { console.error('[cy] _showEdgeEndpoints error:', e); }
};

function _destroyCy() {
    if (window._cy) { window._cy.destroy(); window._cy = null; }
    window._fullElements = [];
}

window._categoryMap = {
    'ownership': ['HOLDS_STAKE_IN', 'SUBSIDIARY_OF'],
    'competition': ['COMPETES_WITH'],
    'roles': ['IS_OFFICER', 'IS_BOARD_MEMBER', 'IS_FOUNDER', 'IS_EXECUTIVE'],
    'industry': ['BELONGS_TO_INDUSTRY'],
    'macro': ['AFFECTS_INDUSTRY', 'HAS_MACRO_INDICATOR'],
    'related_party': ['RELATED_PARTY_TRANSACTION'],
    'guarantees': ['GUARANTEES'],
    'lends_to': ['LENDS_TO'],
    'joint_venture': ['HAS_JOINT_VENTURE_WITH'],
    'underwritten_by': ['UNDERWRITTEN_BY'],
    'cooperation': ['HAS_BUSINESS_COOPERATION'],
    'state_owns': ['STATE_OWNS'],
};

window._filterState = {
    ownership: true,
    competition: true,
    roles: false,
    industry: true,
    macro: true,
    related_party: true,
    guarantees: true,
    lends_to: true,
    joint_venture: true,
    underwritten_by: true,
    cooperation: true,
    state_owns: true,
    search: '',
    nodeType: {
        Company: true,
        Person: false,
        Industry: true,
        MacroIndicator: false,
        Country: false,
    },
    showSubsidiaries: false,
    cartOnly: false,
    cartTickers: [],
    hiddenTickers: [],
};

window._applyFilters = function() {
    if (!window._cy) return;
    try {
        console.log('[cy] _applyFilters called, cy:', !!window._cy, 'ownership:', window._filterState.ownership, 'person:', window._filterState.nodeType && window._filterState.nodeType.Person);
        // Diagnostic: count nodes by type
        var ntypeCounts = {};
        window._cy.nodes().forEach(function(n) { var t = n.data('ntype') || '?'; ntypeCounts[t] = (ntypeCounts[t] || 0) + 1; });
        console.log('[cy] _applyFilters node types in graph:', JSON.stringify(ntypeCounts));
        var fs = window._filterState;
        var q = (fs.search || '').toLowerCase().trim();

        // ── NODES (batch 1): apply type/subsidiary visibility first ──
        //   Must complete BEFORE edges check .visible() — inside a single
        //   batch(), .visible() returns the pre-batch state, so edge
        //   visibility would be wrong if we batch nodes + edges together.
        window._cy.batch(function() {
            window._cy.nodes().forEach(function(node) {
                var ntype = node.data('ntype') || '';
                // Node type filter
                if (fs.nodeType && fs.nodeType[ntype] === false) {
                    node.hide();
                    return;
                }
                // Subsidiary filter
                var companyType = node.data('company_type') || '';
                if (ntype === 'Company' && companyType === 'subsidiary' && !fs.showSubsidiaries) {
                    node.hide();
                    return;
                }
                // Cart-only filter: hide Company nodes not in the cart
                if (fs.cartOnly && fs.cartTickers.length > 0) {
                    var symbol = (node.data('symbol') || '').toUpperCase();
                    var isInCart = fs.cartTickers.some(function(t) {
                        return symbol === t.toUpperCase();
                    });
                    if (ntype === 'Company' && !isInCart) {
                        node.hide();
                        return;
                    }
                }
                // Ticker visibility filter
                if (ntype === 'Company') {
                    var sym = (node.data('symbol') || '').toUpperCase();
                    if (fs.hiddenTickers && fs.hiddenTickers.length > 0 && fs.hiddenTickers.indexOf(sym) >= 0) {
                        node.hide();
                        return;
                    }
                }
                // Show node if it passes all filters — no edge dependency
                node.show();
            });
        });

        // ── EDGES + SEARCH (batch 2): now .visible() sees fresh node state ──
        window._cy.batch(function() {
            window._cy.edges().forEach(function(edge) {
                var rtype = edge.data('rtype') || '';
                var cat = '';
                for (var c in window._categoryMap) {
                    if (window._categoryMap[c].indexOf(rtype) >= 0) { cat = c; break; }
                }
                // Edge is visible only if category enabled AND both endpoints visible
                if (fs[cat] && edge.source().visible() && edge.target().visible()) {
                    edge.show();
                } else {
                    edge.hide();
                }
            });

            // ── SEARCH: highlight matching nodes and zoom to first match ──
            window._cy.nodes().removeClass('highlighted');
            window._cy.nodes().removeClass('match-found');
            if (q) {
                var matches = [];
                window._cy.nodes().forEach(function(node) {
                    var label = (node.data('label') || '').toLowerCase();
                    var symbol = (node.data('symbol') || '').toLowerCase();
                    var nameField = (node.data('name') || '').toLowerCase();
                    if (label.indexOf(q) >= 0 || symbol.indexOf(q) >= 0 || nameField.indexOf(q) >= 0) {
                        node.addClass('highlighted');
                        matches.push(node);
                    }
                });
                if (matches.length > 0) {
                    // Ensure the first match is visible (show its parents/neighbors)
                    window._cy.animate({
                        fit: { eles: matches, padding: 80 },
                        duration: 400,
                        easing: 'ease-in-out-cubic',
                    });
                }
            }
        });
        // ── CART-ONLY: re-show connecting non-Company nodes ──
        if (fs.cartOnly && fs.cartTickers.length > 0) {
            window._cy.batch(function() {
                window._cy.nodes().forEach(function(n) {
                    if (n.visible()) return;
                    if (n.data('ntype') === 'Company') return;
                    var hasVisibleNeighbor = false;
                    n.connectedEdges().forEach(function(e) {
                        if (e.visible()) {
                            var other = e.source().id() === n.id() ? e.target() : e.source();
                            if (other.visible()) hasVisibleNeighbor = true;
                        }
                    });
                    if (hasVisibleNeighbor) n.show();
                });
            });
        }
    } catch(e) { console.error('[cy] _applyFilters error:', e); }
    // Report visible counts to the server
    window._sendVisibleCounts();
};

window._sendVisibleCounts = function() {
    try {
        if (!window._cy) return;
        var visibleNodes = window._cy.nodes(':visible').length;
        var visibleEdges = window._cy.edges(':visible').length;
        if (window._reflexSend) {
            window._reflexSend('graph_state.set_visible_counts', {nodes: visibleNodes, edges: visibleEdges});
        }
    } catch(e) { /* silent */ }
};

window._applyRadialLayout = function() {
    if (!window._cy) return;
    try {
        var visibleNodes = window._cy.nodes(':visible');
        if (visibleNodes.length === 0) return;

        // Build industry → [companies] map from BELONGS_TO_INDUSTRY edges
        var industryNodes = {};
        var industryMembers = {};
        var unaffiliated = [];

        visibleNodes.forEach(function(n) {
            if (n.data('ntype') === 'Industry') {
                industryNodes[n.id()] = n;
                industryMembers[n.id()] = [];
            }
        });

        window._cy.edges(':visible').forEach(function(e) {
            if (e.data('rtype') === 'BELONGS_TO_INDUSTRY') {
                var src = e.source(), tgt = e.target();
                if (src.data('ntype') === 'Industry' && tgt.data('ntype') === 'Company') {
                    industryMembers[src.id()].push(tgt);
                } else if (tgt.data('ntype') === 'Industry' && src.data('ntype') === 'Company') {
                    industryMembers[tgt.id()].push(src);
                }
            }
        });

        // Collect unaffiliated visible nodes (Person nodes, etc.)
        visibleNodes.forEach(function(n) {
            if (n.data('ntype') !== 'Industry') {
                var hasIndustry = false;
                for (var indId in industryMembers) {
                    if (industryMembers[indId].indexOf(n) >= 0) {
                        hasIndustry = true;
                        break;
                    }
                }
                if (!hasIndustry) unaffiliated.push(n);
            }
        });

        var indIds = Object.keys(industryNodes);
        var numIndustries = indIds.length;
        if (numIndustries === 0) return;

        // Big circle for industry nodes — 2x diameter
        var bigRadius = Math.max(700, numIndustries * 120);
        var centerX = 0, centerY = 0;

        indIds.forEach(function(indId, i) {
            var angle = (2 * Math.PI * i) / numIndustries - Math.PI / 2;
            var indX = centerX + bigRadius * Math.cos(angle);
            var indY = centerY + bigRadius * Math.sin(angle);
            industryNodes[indId].position({x: indX, y: indY});

            // Member companies in a ring around their industry — 2x size
            var members = industryMembers[indId];
            var numMembers = members.length;
            var smallRadius = Math.min(320, Math.max(140, numMembers * 20));

            members.forEach(function(company, j) {
                var cAngle = (2 * Math.PI * j) / numMembers;
                company.position({
                    x: indX + smallRadius * Math.cos(cAngle),
                    y: indY + smallRadius * Math.sin(cAngle)
                });
            });
        });

        // Unaffiliated nodes — place near their connected neighbors
        unaffiliated.forEach(function(n, i) {
            var connectedEdges = n.connectedEdges(':visible');
            var connectedNodes = connectedEdges.connectedNodes().filter(function(nei) {
                return nei.visible() && nei.id() !== n.id();
            });

            if (connectedNodes.length > 0) {
                // Average position of connected neighbors
                var sumX = 0, sumY = 0, count = 0;
                connectedNodes.forEach(function(nei) {
                    var pos = nei.position();
                    sumX += pos.x; sumY += pos.y; count++;
                });
                var avgX = sumX / count, avgY = sumY / count;

                // Place near the center of connected nodes with a spread angle
                var angle = (2 * Math.PI * (i % 12)) / 12 + (i * 0.3);
                var offset = 65 + (i % 6) * 12;
                n.position({
                    x: avgX + offset * Math.cos(angle),
                    y: avgY + offset * Math.sin(angle)
                });
            } else {
                // No connections — wide outer ring
                var angle = (2 * Math.PI * i) / Math.max(unaffiliated.length, 1);
                var isolatedRadius = bigRadius + 450 + (i % 4) * 60;
                n.position({
                    x: centerX + isolatedRadius * Math.cos(angle),
                    y: centerY + isolatedRadius * Math.sin(angle)
                });
            }
        });
    } catch(e) { console.error('[cy] _applyRadialLayout error:', e); }
};

window.setSearch = function(query) {
    window._filterState.search = query || '';
    window._applyFilters();
};

window.filterCy = function(searchQuery, showOwnership, showCompetition, showRoles, showIndustry, showMacro, nodeTypeState, showSubsidiaries, showRelatedParty, showGuarantees, showLendsTo, showJointVenture, showUnderwrittenBy, showCooperation, showStateOwns) {
    window._filterState.ownership = showOwnership !== false;
    window._filterState.competition = showCompetition !== false;
    window._filterState.roles = showRoles !== false;
    window._filterState.industry = showIndustry !== false;
    window._filterState.macro = showMacro !== false;
    window._filterState.related_party = showRelatedParty !== false;
    window._filterState.guarantees = showGuarantees !== false;
    window._filterState.lends_to = showLendsTo !== false;
    window._filterState.joint_venture = showJointVenture !== false;
    window._filterState.underwritten_by = showUnderwrittenBy !== false;
    window._filterState.cooperation = showCooperation !== false;
    window._filterState.state_owns = showStateOwns !== false;
    window._filterState.showSubsidiaries = showSubsidiaries === true;
    // Preserve cart-only state (set via _emit_filter_script, not legacy callers)
    if (window._filterState.cartOnly === undefined) window._filterState.cartOnly = false;
    if (!window._filterState.cartTickers) window._filterState.cartTickers = [];
    if (nodeTypeState) {
        window._filterState.nodeType = nodeTypeState;
    }
    window._filterState.search = searchQuery || '';
    var selectedNode = window._cy ? window._cy.nodes(':selected') : null;
    var selectedEdge = window._cy ? window._cy.edges(':selected') : null;
    if (selectedNode && selectedNode.length > 0) {
        window._showImmediateNeighbors(selectedNode[0]);
    } else if (selectedEdge && selectedEdge.length > 0) {
        window._showEdgeEndpoints(selectedEdge[0]);
    } else {
        window._applyFilters();
    }
}

// ── Per-element visibility toggle ──────────────────────────────────────────
window.toggleCyNodeVisibility = function(nodeId) {
    if (!window._cy) return;
    var el = window._cy.getElementById(nodeId);
    if (!el) return;
    var current = parseFloat(el.style('opacity')) || 1;
    el.style('opacity', current >= 1 ? 0.12 : 1);
}

window.toggleCyEdgeVisibility = function(edgeId) {
    if (!window._cy) return;
    var el = window._cy.getElementById(edgeId);
    if (!el) return;
    var current = parseFloat(el.style('opacity')) || 1;
    el.style('opacity', current >= 1 ? 0.12 : 1);
}

// ── Zoom ───────────────────────────────────────────────────────────────────
window.focusEdge = function(edgeId) {
    if (!window._cy) return;
    var edge = window._cy.getElementById(edgeId);
    if (!edge) return;
    window._cy.elements().unselect();
    edge.select();
    var eles = edge.connectedNodes().add(edge);
    window._cy.animate({
        fit: { eles: eles, padding: 60 },
        duration: 200,
        easing: 'ease-in-out-cubic',
    });
}

window.zoomIn = function() {
    if (window._cy) {
        window._cy.zoom({
            level: window._cy.zoom() * 1.3,
            renderedPosition: { x: window.innerWidth/2, y: window.innerHeight/2 }
        });
    }
};
window.zoomOut = function() {
    if (window._cy) {
        window._cy.zoom({
            level: window._cy.zoom() * 0.7,
            renderedPosition: { x: window.innerWidth/2, y: window.innerHeight/2 }
        });
    }
};
window.zoomFit = function() {
    if (window._cy) window._cy.fit(window._cy.nodes(':visible'), 60);
};

// ── Category skeleton overlay (lazy loading indicator) ────────────────────
window._skeletonEl = null;
window.showCategorySkeleton = function(category) {
    window.hideCategorySkeleton();
    var container = document.getElementById('cy-graph');
    if (!container) return;
    var overlay = document.createElement('div');
    overlay.id = 'cy-skeleton-overlay';
    overlay.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;'
        + 'z-index:99;pointer-events:none;display:flex;flex-direction:column;'
        + 'align-items:center;justify-content:flex-start;padding-top:60px;';

    var label = document.createElement('div');
    label.style.cssText = 'display:flex;align-items:center;gap:10px;'
        + 'padding:8px 16px;background:rgba(0,0,0,0.55);'
        + 'border-radius:8px;color:rgba(255,255,255,0.7);'
        + 'font-size:13px;font-family:sans-serif;';
    label.textContent = 'Loading ' + category + ' data' + String.fromCharCode(8230);

    // Three pulsing dots
    var dots = document.createElement('span');
    dots.style.cssText = 'display:inline-flex;gap:4px;';
    for (var i = 0; i < 3; i++) {
        var dot = document.createElement('span');
        dot.style.cssText = 'width:6px;height:6px;border-radius:50%;'
            + 'background:rgba(255,255,255,0.5);display:inline-block;'
            + 'animation:pulse 1.2s ease-in-out ' + (i * 0.2) + 's infinite;';
        dots.appendChild(dot);
    }
    label.appendChild(dots);
    overlay.appendChild(label);
    container.appendChild(overlay);

    // Inject CSS animation if not already present
    if (!document.getElementById('cy-skeleton-style')) {
        var style = document.createElement('style');
        style.id = 'cy-skeleton-style';
        style.textContent = '@keyframes pulse { 0%,100% { opacity:0.2; } 50% { opacity:1; } }';
        document.head.appendChild(style);
    }
    window._skeletonEl = overlay;
};

window.hideCategorySkeleton = function() {
    if (window._skeletonEl && window._skeletonEl.parentNode) {
        window._skeletonEl.parentNode.removeChild(window._skeletonEl);
    }
    window._skeletonEl = null;
};

window.mergeCategoryData = function(newElements) {
    if (!window._cy) return;
    window.hideCategorySkeleton();
    window._cy.add(newElements);
    window._applyFilters();
    // Re-apply radial layout so new nodes get positioned in their
    // industry ring or outer ring. Viewport is **not** reset —
    // no fit() call, user stays where they were looking.
    window._applyRadialLayout();
    window._sendVisibleCounts();
};

// ── Mini preview graph (inside settings dialog, synced with _filterState) ──
window._legendElements = [
    // LEFT — Companies (core entities, vertical)
    { data: { id: 'l-company', label: 'Company A', ntype: 'Company' }, position: { x: 60,  y: 70 } },
    { data: { id: 'l-company2', label: 'Company B', ntype: 'Company' }, position: { x: 60,  y: 240 } },
    // MIDDLE LEFT — Subsidiary (to the right of Company B)
    { data: { id: 'l-subsidiary', label: 'Subsidiary', ntype: 'Company', company_type: 'subsidiary' }, position: { x: 180, y: 240 } },
    // MIDDLE — Person (vertically between Company A and B)
    { data: { id: 'l-person', label: 'Person', ntype: 'Person' }, position: { x: 280, y: 155 } },
    // RIGHT — Industry, Macro, Country (supporting context)
    { data: { id: 'l-industry', label: 'Industry', ntype: 'Industry' }, position: { x: 460, y: 70 } },
    { data: { id: 'l-macro', label: 'Macro', ntype: 'MacroIndicator' }, position: { x: 460, y: 200 } },
    { data: { id: 'l-country', label: 'Country', ntype: 'Country' }, position: { x: 460, y: 330 } },
    // ── Edge categories (show all 12) ──
    { data: { id: 'l-e01', source: 'l-company', target: 'l-person', label: 'ownership', rtype: 'HOLDS_STAKE_IN' } },
    { data: { id: 'l-e02', source: 'l-company', target: 'l-person', label: 'roles', rtype: 'IS_OFFICER' } },
    { data: { id: 'l-e03', source: 'l-company2', target: 'l-company', label: 'competition', rtype: 'COMPETES_WITH' } },
    { data: { id: 'l-e04', source: 'l-company', target: 'l-industry', label: 'industry', rtype: 'BELONGS_TO_INDUSTRY' } },
    { data: { id: 'l-e05', source: 'l-macro', target: 'l-country', label: 'macro', rtype: 'HAS_MACRO_INDICATOR' } },
    { data: { id: 'l-e06', source: 'l-person', target: 'l-company2', label: 'related party', rtype: 'RELATED_PARTY_TRANSACTION' } },
    { data: { id: 'l-e07', source: 'l-company', target: 'l-company2', label: 'guarantees', rtype: 'GUARANTEES' } },
    { data: { id: 'l-e08', source: 'l-company2', target: 'l-company', label: 'lends to', rtype: 'LENDS_TO' } },
    { data: { id: 'l-e09', source: 'l-company', target: 'l-company2', label: 'joint venture', rtype: 'HAS_JOINT_VENTURE_WITH' } },
    { data: { id: 'l-e10', source: 'l-company2', target: 'l-company', label: 'underwritten by', rtype: 'UNDERWRITTEN_BY' } },
    { data: { id: 'l-e11', source: 'l-company', target: 'l-company2', label: 'cooperation', rtype: 'HAS_BUSINESS_COOPERATION' } },
    { data: { id: 'l-e12', source: 'l-company', target: 'l-company2', label: 'state owns', rtype: 'STATE_OWNS' } },
    // Subsidiary: Company B → Subsidiary
    { data: { id: 'l-e13', source: 'l-company2', target: 'l-subsidiary', label: 'ownership', rtype: 'HOLDS_STAKE_IN' } },
];

window._syncLegend = function() {
    if (!window._legendCy) return;
    var fs = window._filterState;
    if (!fs) return;
    window._legendCy.batch(function() {
        // Node visibility by type
        window._legendCy.nodes().forEach(function(n) {
            var ntype = n.data('ntype') || '';
            if (fs.nodeType && fs.nodeType[ntype] === false) {
                n.style({ 'opacity': 0.08, 'label': '' });
            } else {
                n.style({ 'opacity': 1, 'label': 'data(label)' });
                // Subsidiary filter (company_type === 'subsidiary')
                var ctype = n.data('company_type') || '';
                if (ctype === 'subsidiary' && fs.showSubsidiaries === false) {
                    n.style({ 'opacity': 0.08, 'label': '' });
                }
            }
        });

        // Edge visibility by category + endpoint visibility
        function _hasCat(rtype) {
            for (var c in window._categoryMap) {
                if (window._categoryMap[c].indexOf(rtype) >= 0) return c;
            }
            return null;
        }
        window._legendCy.edges().forEach(function(e) {
            var rtype = e.data('rtype') || '';
            var cat = _hasCat(rtype);
            var srcVis = e.source().style('opacity') > 0.5;
            var tgtVis = e.target().style('opacity') > 0.5;
            if (cat && fs[cat] && srcVis && tgtVis) {
                e.style({ 'opacity': 1, 'label': 'data(label)' });
            } else {
                e.style({ 'opacity': 0.08, 'label': '' });
            }
        });
    });
};

window.initCyLegend = function() {
    var container = document.getElementById('cy-legend');
    if (!container) {
        console.log('[legend] container not found, retrying...');
        setTimeout(window.initCyLegend, 200);
        return;
    }
    if (typeof cytoscape === 'undefined') {
        setTimeout(window.initCyLegend, 200);
        return;
    }

    // Wait until the container has proper dimensions (dialog may still be animating)
    if (!container.clientWidth || !container.clientHeight) {
        setTimeout(window.initCyLegend, 150);
        return;
    }

    // If instance exists and is still attached to same container, just re-center
    if (window._legendCy) {
        if (window._legendCy.container() === container) {
            // Same container — just re-center and update filters
            window._legendCy.resize();
            window._legendCy.fit(undefined, 35);
            window._syncLegend();
            return;
        }
        // Container was replaced (Reflex re-render), destroy old instance
        window._legendCy.destroy();
        window._legendCy = null;
    }

    window._legendCy = cytoscape({
        container: container,
        elements: window._legendElements,
        style: _buildCyStyle(),
        layout: { name: 'preset' },
        boxSelectionEnabled: false,
        autoungrabify: true,
        autounselectify: true,
    });

    // Center: resize -> fit -> lock -> apply filters
    function _doCenter() {
        if (!window._legendCy || !container.clientWidth) {
            setTimeout(_doCenter, 100);
            return;
        }
        window._legendCy.resize();
        window._legendCy.fit(undefined, 35);
        window._legendCy.userZoomingEnabled(false);
        window._legendCy.userPanningEnabled(false);
        window._syncLegend();
        console.log('[legend] centered at', container.clientWidth, 'x', container.clientHeight);
    }
    _doCenter();
    // Re-center after dialog transition completes (animations can shift layout)
    setTimeout(_doCenter, 500);
};
"""
