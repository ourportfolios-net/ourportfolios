"""Cytoscape.js JavaScript engine embedded as a Python string for rx.script."""

_CYTOSCAPE_JS = """
// ── Cytoscape.js Graph Engine ──────────────────────────────────────────────
window._cy = null;
window._fullElements = [];

// ── Edge label helpers ────────────────────────────────────────────────────
function _edgeLabel(rtype) {
    var map = {
        'HOLDS_STAKE_IN': 'owns',
        'SUBSIDIARY_OF': 'subsidiary',
        'COMPETES_WITH': 'competes',
        'IS_OFFICER': 'officer',
        'IS_BOARD_MEMBER': 'board member',
        'IS_FOUNDER': 'founder',
        'IS_EXECUTIVE': 'executive',
        'BELONGS_TO': 'belongs to',
        'BELONGS_TO_INDUSTRY': 'belongs to',
        'AFFECTS_SECTOR': 'affects',
        'AFFECTS_INDUSTRY': 'affects',
        'HAS_MACRO_INDICATOR': 'macro',
        'AUDITED_BY': 'audited by',
        'RELATED_PARTY_TRANSACTION': 'related party',
        'GUARANTEES': 'guarantees',
        'LENDS_TO': 'lends to',
        'HAS_JOINT_VENTURE_WITH': 'joint venture',
        'UNDERWRITTEN_BY': 'underwritten by',
        'HAS_BUSINESS_COOPERATION': 'cooperation',
        'STATE_OWNS': 'state owns',
    };
    return map[rtype] || rtype.replace(/_/g, ' ');
}

function _edgeArrow(rtype) {
    if (rtype === 'HOLDS_STAKE_IN' || rtype === 'SUBSIDIARY_OF') return 'diamond';
    if (rtype === 'COMPETES_WITH') return 'tee';
    if (rtype === 'IS_OFFICER' || rtype === 'IS_BOARD_MEMBER' || rtype === 'IS_FOUNDER' || rtype === 'IS_EXECUTIVE' || rtype === 'AUDITED_BY') return 'triangle';
    if (rtype === 'BELONGS_TO' || rtype === 'BELONGS_TO_INDUSTRY') return 'none';
    if (rtype === 'AFFECTS_SECTOR' || rtype === 'AFFECTS_INDUSTRY' || rtype === 'HAS_MACRO_INDICATOR') return 'circle';
    return 'triangle';
}

function _edgeLineStyle(rtype) {
    if (rtype === 'COMPETES_WITH') return 'dashed';
    if (rtype === 'AFFECTS_SECTOR' || rtype === 'AFFECTS_INDUSTRY' || rtype === 'HAS_MACRO_INDICATOR') return 'dotted';
    if (rtype === 'AUDITED_BY') return 'solid';
    return 'solid';
}

function _edgeWidth(rtype) {
    if (rtype === 'HOLDS_STAKE_IN' || rtype === 'SUBSIDIARY_OF') return 2.5;
    if (rtype === 'COMPETES_WITH') return 2;
    if (rtype === 'IS_OFFICER' || rtype === 'IS_BOARD_MEMBER' || rtype === 'IS_FOUNDER' || rtype === 'IS_EXECUTIVE' || rtype === 'AUDITED_BY') return 1.5;
    if (rtype === 'BELONGS_TO' || rtype === 'BELONGS_TO_INDUSTRY') return 1;
    if (rtype === 'AFFECTS_SECTOR' || rtype === 'AFFECTS_INDUSTRY' || rtype === 'HAS_MACRO_INDICATOR') return 1.5;
    return 1.5;
}

function _edgeOpacity(rtype) {
    if (rtype === 'BELONGS_TO' || rtype === 'BELONGS_TO_INDUSTRY') return 0.5;
    if (rtype === 'AFFECTS_SECTOR' || rtype === 'AFFECTS_INDUSTRY' || rtype === 'HAS_MACRO_INDICATOR') return 0.6;
    return 0.8;
}

// ── Node label helpers ────────────────────────────────────────────────────
function _nodeFontSize(ntype) {
    if (ntype === 'Company') return '13px';
    if (ntype === 'Sector' || ntype === 'Industry') return '12px';
    return '11px';
}

function _deriveLabel(id) {
    // e.g. "Company:HPG" → "HPG", "Person:John" → "John"
    var idx = id.lastIndexOf(':');
    if (idx >= 0 && idx < id.length - 1) return id.substring(idx + 1);
    return id;
}

// ── Style builder ─────────────────────────────────────────────────────────
function _buildCyStyle() {
    const nodeColors = window._nodeColors || {};
    const nodeShapes = window._nodeShapes || {};
    const companyTypeColors = window._companyTypeColors || {};
    const relColors = window._relColors || {};
    const relStyles = window._relStyles || {};

    const nodeStyles = Object.entries(nodeColors).map(function(entry) {
        var ntype = entry[0];
        var color = entry[1];
        return {
            selector: 'node[ntype="' + ntype + '"]',
            style: {
                'background-color': color,
                'shape': nodeShapes[ntype] || 'ellipse',
                'label': 'data(label)',
                'font-size': _nodeFontSize(ntype),
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

    // Company type color overrides (subsidiaries, audit firms get muted colors)
    Object.entries(companyTypeColors).forEach(function(entry) {
        var ctype = entry[0];
        var color = entry[1];
        nodeStyles.push({
            selector: 'node[ntype="Company"][company_type="' + ctype + '"]',
            style: { 'background-color': color }
        });
    });

    // Sector/Industry get centered labels (inside the node)
    nodeStyles.push({
        selector: 'node[ntype="Sector"], node[ntype="Industry"]',
        style: {
            'text-valign': 'center',
            'text-halign': 'center',
            'text-margin-y': 0,
        }
    });

    var edgeStyles = Object.entries(relColors).map(function(entry) {
        var rtype = entry[0];
        var color = entry[1];
        var lstyle = relStyles[rtype] || _edgeLineStyle(rtype);
        return {
            selector: 'edge[rtype="' + rtype + '"]',
            style: {
                'line-color': color,
                'target-arrow-color': color,
                'target-arrow-shape': _edgeArrow(rtype),
                'line-style': lstyle,
                'width': _edgeWidth(rtype),
                'line-opacity': _edgeOpacity(rtype),
                'curve-style': (rtype === 'HOLDS_STAKE_IN' || rtype === 'SUBSIDIARY_OF') ? 'bezier' : 'haystack',
                'label': 'data(label)',
                'font-size': '7px',
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
                    'width': 'mapData(size, 0, 100, 20, 50)',
                    'height': 'mapData(size, 0, 100, 20, 50)',
                    'border-width': 2,
                    'border-color': '#1e293b',
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

function _formatElements(graphJson) {
    var data = typeof graphJson === 'string' ? JSON.parse(graphJson) : graphJson;
    if (!data || !data.nodes) return [];

    var elements = [];
    var i, node, edge, ntype, props, label, degree, eid;

    for (i = 0; i < data.nodes.length; i++) {
        node = data.nodes[i];
        ntype = (node.labels && node.labels[0]) || 'Unknown';
        props = node.properties || {};
        label = props.name || props.person_name || props.symbol || _deriveLabel(node.id);
        degree = data.edges
            ? data.edges.filter(function(e) { return e.source === node.id || e.target === node.id; }).length
            : 0;
        elements.push({
            group: 'nodes',
            data: Object.assign({}, props, {
                id: node.id,
                label: label,
                ntype: ntype,
                size: Math.min(50, Math.max(20, 15 + degree * 3)),
            })
        });
    }

    for (i = 0; i < data.edges.length; i++) {
        edge = data.edges[i];
        eid = edge.source + '--' + edge.relationship + '--' + edge.target;
        if (edge.properties && edge.properties.stake_percent) {
            eid += '--' + edge.properties.stake_percent;
        }
        elements.push({
            group: 'edges',
            data: Object.assign({}, (edge.properties || {}), {
                id: eid,
                source: edge.source,
                target: edge.target,
                rtype: edge.relationship,
                label: _edgeLabel(edge.relationship),
            })
        });
    }

    return elements;
}

window.initCyGraph = function(graphJson) {
    _destroyCy();
    var container = document.getElementById('cy-graph');
    if (!container) return;

    window._fullElements = _formatElements(graphJson);
    window._cy = cytoscape({
        container: container,
        elements: window._fullElements,
        style: _buildCyStyle(),
        layout: {
            name: 'cose',
            animate: 'end',
            animationDuration: 800,
            nodeRepulsion: 12000,
            idealEdgeLength: 120,
            edgeElasticity: 80,
            gravity: 0.3,
            numIter: 1500,
            coolingFactor: 0.9,
            minTemp: 0.5,
            padding: 40,
        },
        minZoom: 0.15,
        maxZoom: 5,
        wheelSensitivity: 0.4,
    });

    // Apply default filters (hide financial edges, etc.)
    window._applyFilters();

    window._cy.on('tap', 'node', function(evt) {
        var node = evt.target;
        var nodeId = node.id();
        window._cy.nodes().unselect();
        window._cy.edges().unselect();
        node.select();
        // Connected-component highlight
        window._showConnectedComponent(node);
        if (window._reflexSend) {
            window._reflexSend('graph_state.handle_node_click', {node_id: nodeId});
        }
    });

    window._cy.on('tap', 'edge', function(evt) {
        var edge = evt.target;
        var edgeId = edge.id();
        window._cy.nodes().unselect();
        window._cy.edges().unselect();
        edge.select();
        // Keep connected component visible when inspecting an edge
        if (window._reflexSend) {
            window._reflexSend('graph_state.handle_edge_click', {edge_id: edgeId});
        }
    });

    window._cy.on('tap', function(evt) {
        if (evt.target === window._cy) {
            window._cy.nodes().unselect();
            window._cy.edges().unselect();
            // Clear component highlight — show everything again
            window._cy.elements().show();
            if (window._reflexSend) {
                window._reflexSend('graph_state.handle_background_click', {});
            }
        }
    });
}

window._showConnectedComponent = function(startNode) {
    if (!window._cy) return;
    // BFS to find all nodes reachable from startNode
    var visited = {};
    var queue = [startNode];
    visited[startNode.id()] = true;
    while (queue.length > 0) {
        var current = queue.shift();
        current.connectedEdges().forEach(function(edge) {
            var other = edge.source().id() === current.id() ? edge.target() : edge.source();
            if (!visited[other.id()]) {
                visited[other.id()] = true;
                queue.push(other);
            }
        });
    }
    // First, apply category filters to edges (respect user toggles)
    window._cy.batch(function() {
        window._cy.edges().forEach(function(edge) {
            var rtype = edge.data('rtype') || '';
            var cat = 'other';
            for (var c in window._categoryMap) {
                if (window._categoryMap[c].indexOf(rtype) >= 0) { cat = c; break; }
            }
            if (cat === 'other' || window._filterState[cat]) {
                edge.show();
            } else {
                edge.hide();
            }
        });
        // Show only nodes in the connected component that have visible edges
        window._cy.nodes().forEach(function(node) {
            if (visited[node.id()]) {
                var hasVisible = false;
                node.connectedEdges().forEach(function(e) { if (e.visible()) hasVisible = true; });
                if (hasVisible) { node.show(); } else { node.hide(); }
            } else {
                node.hide();
            }
        });
    });
    // Fit the view
    var component = window._cy.nodes(':visible');
    if (component.length > 0) {
        window._cy.animate({
            fit: { eles: component, padding: 50 },
            duration: 200,
            easing: 'ease-in-out-cubic',
        });
    }
};

function _destroyCy() {
    if (window._cy) { window._cy.destroy(); window._cy = null; }
    window._fullElements = [];
}

window._categoryMap = {
    'ownership': ['HOLDS_STAKE_IN', 'SUBSIDIARY_OF'],
    'competition': ['COMPETES_WITH'],
    'roles': ['IS_OFFICER', 'IS_BOARD_MEMBER', 'IS_FOUNDER', 'IS_EXECUTIVE', 'AUDITED_BY'],
    'industry': ['BELONGS_TO', 'BELONGS_TO_INDUSTRY'],
    'macro': ['AFFECTS_SECTOR', 'AFFECTS_INDUSTRY', 'HAS_MACRO_INDICATOR'],
};

window._filterState = {
    ownership: true,
    competition: true,
    roles: true,
    industry: true,
    macro: false,
    financial: false,  // hidden by default — utility edges
    search: '',
};

window._applyFilters = function() {
    if (!window._cy) return;
    var fs = window._filterState;
    var q = (fs.search || '').toLowerCase().trim();

    window._cy.batch(function() {
        window._cy.edges().forEach(function(edge) {
            var rtype = edge.data('rtype') || '';
            var cat = 'other';
            for (var c in window._categoryMap) {
                if (window._categoryMap[c].indexOf(rtype) >= 0) { cat = c; break; }
            }
            if (cat === 'other' || fs[cat]) {
                edge.show();
            } else {
                edge.hide();
            }
        });

        // Show nodes that have at least one visible edge, plus search matches
        window._cy.nodes().forEach(function(node) {
            var hasVisibleEdge = false;
            node.connectedEdges().forEach(function(e) { if (e.visible()) hasVisibleEdge = true; });
            if (hasVisibleEdge) {
                node.show();
            } else if (q) {
                var label = (node.data('label') || '').toLowerCase();
                var ntype = (node.data('ntype') || '').toLowerCase();
                if (label.indexOf(q) >= 0 || ntype.indexOf(q) >= 0) {
                    node.show();
                    return;
                }
                node.hide();
            } else {
                node.hide();
            }
        });

        // Highlight search matches
        window._cy.nodes().removeClass('highlighted');
        if (q) {
            window._cy.nodes().forEach(function(node) {
                var label = (node.data('label') || '').toLowerCase();
                var ntype = (node.data('ntype') || '').toLowerCase();
                if (label.indexOf(q) >= 0 || ntype.indexOf(q) >= 0) {
                    node.addClass('highlighted');
                }
            });
        }
    });
};

window.setFilter = function(category, enabled) {
    window._filterState[category] = enabled;
    // Clear component highlight, apply global filters, then
    // re-highlight if a node is selected.
    var selected = window._cy ? window._cy.nodes(':selected') : null;
    window._cy.elements().show();
    window._applyFilters();
    if (selected && selected.length > 0) {
        window._showConnectedComponent(selected[0]);
    }
};

window.setSearch = function(query) {
    window._filterState.search = query || '';
    window._applyFilters();
};

window.filterCy = function(searchQuery, showOwnership, showCompetition, showRoles, showIndustry, showMacro) {
    // Legacy bridge — maps the old Reflex state to new filter system
    window._filterState.ownership = showOwnership !== false;
    window._filterState.competition = showCompetition !== false;
    window._filterState.roles = showRoles !== false;
    window._filterState.industry = showIndustry !== false;
    window._filterState.macro = showMacro !== false;
    window._filterState.search = searchQuery || '';
    // Re-apply component highlight if a node is selected
    var selected = window._cy ? window._cy.nodes(':selected') : null;
    if (selected && selected.length > 0) {
        window._showConnectedComponent(selected[0]);
    } else {
        window._applyFilters();
    }
}

// ── Per-element visibility toggle (eye / eye-off) ──────────────────────────
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

// ── Zoom to a specific edge ────────────────────────────────────────────────
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
"""
