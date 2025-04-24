import React, { useRef, useEffect, useState } from 'react';
import * as d3 from 'd3';
import chromosomeData from './data/chromosome_data.json';

const geneColors = [
  '#4F81BD', '#C0504D', '#9BBB59', '#8064A2', '#F79646',
  '#2C4D75', '#9E480E', '#77933C', '#604A7B', '#C00000'
];

const baseColors = {
  A: '#1f77b4', // blue
  C: '#2ca02c', // green
  T: '#d62728', // red
  G: '#ff7f0e'  // orange
};

// Define AND EXPORT the data object using a NAMED export
export const realChromosome = {
  name: chromosomeData.name,
  length: chromosomeData.length,
  genes: []
};

const realSequence = chromosomeData.sequence.toUpperCase().replace(/[^ACGT]/g, ''); // Ensure clean sequence

window._realChromosome = realChromosome;
window._realSequence = realSequence;

// Assign color to gene by index (alternating from 10 colors)
function getGeneColor(index) {
  return geneColors[index % geneColors.length];
}

function numberWithCommas(x) {
  return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

function GenomeBrowser({ genes }) {
  realChromosome.genes = genes;

  const overviewRef = useRef();
  const detailRef = useRef();
  const zoomRef = useRef();
  // Initialize state with the length from the JSON data
  const [zoomRegion, setZoomRegion] = useState([0, realChromosome.length]);
  const [hoveredGene, setHoveredGene] = useState(null);
  const [selectedGene, setSelectedGene] = useState(null);

  // --- D3 Zoom Setup: Only once on mount ---
  useEffect(() => {
    const width = window.innerWidth;
    const detailHeight = 80;
    const margin = { left: 60, right: 60 };
    const minZoom = 1;
    // Maximum zoom: allow 1bp per 1.25px (double again)
    const visiblePixels = width - margin.left - margin.right;
    const minBpWindow = visiblePixels / 20; // at max zoom, show 1bp per 1.25px
    const maxZoom = realChromosome.length / minBpWindow;
    const zoom = d3.zoom()
      .scaleExtent([minZoom, maxZoom])
      .translateExtent([[margin.left, 0], [width - margin.right, detailHeight]])
      .extent([[margin.left, 0], [width - margin.right, detailHeight]])
      .on('zoom', (event) => {
        const t = event.transform;
        const x = d3.scaleLinear().domain([0, realChromosome.length]).range([margin.left, width - margin.left - margin.right]);
        const newDomain = t.rescaleX(x).domain();
        let newRegion = [
          Math.max(0, newDomain[0]),
          Math.min(realChromosome.length, newDomain[1])
        ];
        if (newRegion[0] <= 0 + 1 && newRegion[1] >= realChromosome.length - 1) {
          newRegion = [0, realChromosome.length];
        }
        // Only update if region actually changed, to avoid infinite loop
        setZoomRegion(prev => {
          if (
            Math.abs(newRegion[0] - prev[0]) > 0.5 ||
            Math.abs(newRegion[1] - prev[1]) > 0.5
          ) {
            return newRegion;
          }
          return prev;
        });
      });
    d3.select(detailRef.current).call(zoom);
    zoomRef.current = zoom;
    d3.select(detailRef.current).call(zoom.transform, d3.zoomIdentity);
    d3.select(detailRef.current).on('dblclick.zoom', null);
    d3.select(detailRef.current).on('dblclick.reset', () => {
      d3.select(detailRef.current).transition().duration(300).call(zoom.transform, d3.zoomIdentity);
      setZoomRegion([0, realChromosome.length]);
    });
    // eslint-disable-next-line
  }, []);

  // Synchronize d3 zoom transform with zoomRegion changes (from slider/tool)
  useEffect(() => {
    if (!zoomRef.current || !detailRef.current) return;
    const width = window.innerWidth;
    const margin = { left: 60, right: 60 };
    const x = d3.scaleLinear().domain([0, realChromosome.length]).range([margin.left, width - margin.left - margin.right]);
    const k = (realChromosome.length / (zoomRegion[1] - zoomRegion[0]));
    const tx = -x(zoomRegion[0]) * k + margin.left;
    const transform = d3.zoomIdentity.translate(tx, 0).scale(k);
    // Only update transform if not already at this zoom
    const currentTransform = d3.zoomTransform(detailRef.current);
    if (
      Math.abs(currentTransform.k - k) > 0.01 ||
      Math.abs(currentTransform.x - tx) > 0.5
    ) {
      d3.select(detailRef.current).call(zoomRef.current.transform, transform);
    }
  }, [zoomRegion]);

  // --- Draw both SVGs whenever zoomRegion changes ---
  useEffect(() => {
    // Get available width accounting for chat panel
    const availableWidth = window.innerWidth;
    const overviewHeight = 80;
    const detailHeight = 100;
    const margin = { left: 60, right: 60 };

    // -- OVERVIEW BAR --
    d3.select(overviewRef.current).selectAll('*').remove();
    const overviewSvg = d3.select(overviewRef.current)
      .attr('width', availableWidth)
      .attr('height', overviewHeight)
      .style('background', '#f8f8fa');
    const xOverview = d3.scaleLinear()
      .domain([0, realChromosome.length])
      .range([margin.left, availableWidth - margin.right]);
    // Chromosome bar (move lower)
    const overviewBarY = 32; // was 12, now lower 
    overviewSvg.append('rect')
      .attr('x', margin.left)
      .attr('y', overviewBarY)
      .attr('width', availableWidth - margin.left - margin.right)
      .attr('height', 16)
      .attr('rx', 10)
      .attr('fill', '#cccccc');

    // Genes
    overviewSvg.selectAll('.gene')
      .data(realChromosome.genes) // Use realChromosome.genes
      .enter()
      .append('rect')
      .attr('class', 'gene')
      .attr('x', d => xOverview(d.start))
      .attr('y', overviewBarY + 1)
      .attr('width', d => Math.max(1, xOverview(d.end) - xOverview(d.start)))
      .attr('height', 14)
      .attr('fill', (d, i) => getGeneColor(i))
      .attr('rx', 5);
    // Red rectangle for zoom region
    const isFullView = zoomRegion[0] <= 0 + 1 && zoomRegion[1] >= realChromosome.length - 1;

    // Draggable zoom rectangle
    const dragZoomRect = d3.drag()
      .on('start', function (event) {
        d3.select(this).attr('cursor', 'grabbing');
        // Store the initial click offset from the rectangle's left edge
        const rectX = parseFloat(d3.select(this).attr('x'));
        d3.select(this).attr('data-offset', event.x - rectX);
      })
      .on('drag', function (event) {
        if (isFullView) return; // Don't drag when showing full view

        const width = parseFloat(d3.select(this).attr('width'));
        const offset = parseFloat(d3.select(this).attr('data-offset')) || 0;

        // Apply the offset to maintain grab position
        const adjustedX = event.x - offset;

        const minX = margin.left;
        const maxX = availableWidth - margin.right - width;

        // Constrain to chromosome boundaries
        let newX = Math.max(minX, Math.min(maxX, adjustedX));

        // Update rectangle position
        d3.select(this).attr('x', newX);

        // Calculate new zoom region based on drag position
        const newStart = xOverview.invert(newX);
        const newEnd = xOverview.invert(newX + width);

        // Update zoom region if significantly different (avoid unnecessary updates)
        if (Math.abs(newStart - zoomRegion[0]) > 1 || Math.abs(newEnd - zoomRegion[1]) > 1) {
          setZoomRegion([newStart, newEnd]);
        }
      })
      .on('end', function () {
        d3.select(this).attr('cursor', 'grab');
      });

    const zoomRect = overviewSvg.append('rect')
      .attr('class', 'zoom-rect')
      .attr('x', isFullView ? margin.left : xOverview(zoomRegion[0]))
      .attr('y', overviewBarY - 5)
      .attr('width', isFullView ? (availableWidth - margin.left - margin.right) : (xOverview(zoomRegion[1]) - xOverview(zoomRegion[0])))
      .attr('height', 26)
      .attr('fill', 'rgba(255, 0, 0, 0.1)')  // Semi-transparent red fill
      .attr('stroke', 'red')
      .attr('stroke-width', 2)
      .attr('cursor', 'grab')
      .style('pointer-events', 'all');  // Make sure pointer events work on the entire rectangle

    // Add drag behavior if not showing full view
    if (!isFullView) {
      zoomRect.call(dragZoomRect);
    }

    // Make genes easier to select in overview
    overviewSvg.selectAll('.gene-hitbox')
      .data(realChromosome.genes)
      .enter()
      .append('rect')
      .attr('class', 'gene-hitbox')
      .attr('x', d => Math.max(margin.left, xOverview(d.start) - 5))
      .attr('y', overviewBarY - 4)
      .attr('width', d => Math.max(10, xOverview(d.end) - xOverview(d.start) + 10))
      .attr('height', 24)
      .attr('fill', 'transparent')
      .attr('cursor', 'pointer')
      .style('pointer-events', 'all')
      .on('mouseover', function (event, d) {
        setSelectedGene(null); // Clear selection when hovering a new gene
        setHoveredGene(d);

        // Highlight the actual gene
        overviewSvg.selectAll('.gene')
          .filter(g => g === d)
          .attr('stroke', '#000')
          .attr('stroke-width', 1);
      })
      .on('mouseout', function () {
        setHoveredGene(null);

        // Remove highlight
        overviewSvg.selectAll('.gene')
          .attr('stroke', 'none');
      })
      .on('click', function (event, d) {
        event.stopPropagation();
        setSelectedGene(d);
      });

    // --- SCALES for + strand (overview bar, above the bar) ---
    const overviewTicks = xOverview.ticks(10).filter(t => t >= 0 && t <= realChromosome.length);
    overviewSvg.selectAll('.overview-scale-plus')
      .data(overviewTicks)
      .enter()
      .append('line')
      .attr('class', 'overview-scale-plus')
      .attr('x1', d => xOverview(d))
      .attr('x2', d => xOverview(d))
      .attr('y1', overviewBarY - 12)
      .attr('y2', overviewBarY - 8)
      .attr('stroke', '#555')
      .attr('stroke-width', 1);
    overviewSvg.selectAll('.overview-scale-plus-label')
      .data(overviewTicks)
      .enter()
      .append('text')
      .attr('class', 'overview-scale-plus-label')
      .attr('x', d => xOverview(d))
      .attr('y', overviewBarY - 16)
      .attr('text-anchor', 'middle')
      .attr('font-size', 11)
      .attr('fill', '#555')
      .text(d => numberWithCommas(Math.round(d)));

    // -- DETAIL BAR --
    d3.select(detailRef.current).selectAll('*').remove();
    const detailSvg = d3.select(detailRef.current)
      .attr('width', availableWidth)
      .attr('height', detailHeight + 40)
      .style('background', '#fff');
    // Scales
    const xDetail = d3.scaleLinear()
      .domain(zoomRegion)
      .range([margin.left, availableWidth - margin.right]);
    // Add a clipPath for the chromosome bar area (now tall enough for genes below)
    const chrBarY = 20;
    const chrBarH = 24;
    const geneLineGap = 24; // Increased from 10 to add more space
    const clipHeight = chrBarH + geneLineGap * 2 + 18 + 12 + 20; // Increased height for more space
    detailSvg.append('clipPath')
      .attr('id', 'detail-clip')
      .append('rect')
      .attr('x', margin.left)
      .attr('y', chrBarY)
      .attr('width', availableWidth - margin.left - margin.right)
      .attr('height', clipHeight);
    // Chromosome bar
    // Remove rounded corners except at chromosome ends
    const isAtChromStart = Math.abs(zoomRegion[0] - 0) < 1;
    const isAtChromEnd = Math.abs(zoomRegion[1] - realChromosome.length) < 1;
    let rxLeft = isAtChromStart ? 10 : 0;
    let rxRight = isAtChromEnd ? 10 : 0;
    // SVG only supports one rx, so we use a path for custom corners
    if (rxLeft !== rxRight) {
      // Draw as path for mixed corners
      const barX = margin.left;
      const barW = availableWidth - margin.left - margin.right;
      let d = '';
      d += `M${barX + rxLeft},${chrBarY}`;
      d += `H${barX + barW - rxRight}`;
      if (rxRight) {
        d += `A${rxRight},${rxRight} 0 0 1 ${barX + barW},${chrBarY + rxRight}`;
        d += `V${chrBarY + chrBarH - rxRight}`;
        d += `A${rxRight},${rxRight} 0 0 1 ${barX + barW - rxRight},${chrBarY + chrBarH}`;
      } else {
        d += `V${chrBarY + chrBarH}`;
      }
      d += `H${barX + rxLeft}`;
      if (rxLeft) {
        d += `A${rxLeft},${rxLeft} 0 0 1 ${barX},${chrBarY + chrBarH - rxLeft}`;
        d += `V${chrBarY + rxLeft}`;
        d += `A${rxLeft},${rxLeft} 0 0 1 ${barX + rxLeft},${chrBarY}`;
      } else {
        d += `V${chrBarY}`;
      }
      d += 'Z';
      detailSvg.append('path')
        .attr('d', d)
        .attr('fill', '#cccccc')
        .attr('class', 'chr-bar');
    } else {
      detailSvg.append('rect')
        .attr('class', 'chr-bar')
        .attr('x', margin.left)
        .attr('y', chrBarY)
        .attr('width', availableWidth - margin.left - margin.right)
        .attr('height', chrBarH)
        .attr('rx', rxLeft)
        .attr('fill', '#cccccc');
    }

    // --- TRACK LINES for gene rows ---
    detailSvg.append('line')
      .attr('x1', margin.left)
      .attr('x2', availableWidth - margin.right)
      .attr('y1', 54)
      .attr('y2', 54)
      .attr('stroke', '#b0b0b0')
      .attr('stroke-width', 1);
    detailSvg.append('line')
      .attr('x1', margin.left)
      .attr('x2', availableWidth - margin.right)
      .attr('y1', 84) // Increased from 72 to add more space
      .attr('y2', 84) // Increased from 72 to add more space
      .attr('stroke', '#b0b0b0')
      .attr('stroke-width', 1);

    // --- GENES WITH ARROWS ---
    // Helper to draw an arrow for a gene (SVG path)
    function geneArrowPath(x1, x2, y, height, strand) {
      const w = Math.abs(x2 - x1);
      if (w < 12) return `M${x1},${y} h${w}`; // too small for arrow
      if (strand === '+') {
        return `M${x1},${y} h${w - 7} l4,-5 l0,10 l-4,-5 h7`;
      } else {
        return `M${x2},${y} h-${w - 7} l-4,-5 l0,10 l4,-5 h-7`;
      }
    }
    // Draw + strand genes as arrows
    const plusGenes = realChromosome.genes.filter(g => g.strand === '+');
    detailSvg.selectAll('.gene-plus-arrow')
      .data(plusGenes)
      .enter()
      .append('path')
      .attr('class', 'gene-plus-arrow')
      .attr('d', (d, i) => geneArrowPath(xDetail(d.start), xDetail(d.end), 54, 12, '+'))
      .attr('stroke', (d, i) => getGeneColor(realChromosome.genes.indexOf(d)))
      .attr('stroke-width', 8)
      .attr('fill', 'none')
      .attr('clip-path', 'url(#detail-clip)')
      .attr('opacity', 0.75)
      .on('mouseover', function (event, d) {
        setSelectedGene(null); // Clear selection when hovering a new gene
        setHoveredGene(d);
      })
      .on('mouseout', function () {
        setHoveredGene(null);
      })
      .on('click', function (event, d) {
        event.stopPropagation(); // Prevent triggering background click
        setSelectedGene(d);
      });
    // Draw - strand genes as arrows
    const minusGenes = realChromosome.genes.filter(g => g.strand === '-');
    detailSvg.selectAll('.gene-minus-arrow')
      .data(minusGenes)
      .enter()
      .append('path')
      .attr('class', 'gene-minus-arrow')
      .attr('d', (d, i) => geneArrowPath(xDetail(d.start), xDetail(d.end), 84, 12, '-')) // Increased from 72 to add more space
      .attr('stroke', (d, i) => getGeneColor(realChromosome.genes.indexOf(d)))
      .attr('stroke-width', 8)
      .attr('fill', 'none')
      .attr('clip-path', 'url(#detail-clip)')
      .attr('opacity', 0.75)
      .on('mouseover', function (event, d) {
        setSelectedGene(null); // Clear selection when hovering a new gene
        setHoveredGene(d);
      })
      .on('mouseout', function () {
        setHoveredGene(null);
      })
      .on('click', function (event, d) {
        event.stopPropagation(); // Prevent triggering background click
        setSelectedGene(d);
      });

    // Add hit areas for genes in detail view
    detailSvg.selectAll('.gene-plus-hitbox')
      .data(plusGenes)
      .enter()
      .append('rect')
      .attr('class', 'gene-plus-hitbox')
      .attr('x', d => Math.max(margin.left, xDetail(d.start) - 5))
      .attr('y', 44) // Above the gene arrow
      .attr('width', d => Math.max(10, xDetail(d.end) - xDetail(d.start) + 10))
      .attr('height', 20)
      .attr('fill', 'transparent')
      .attr('cursor', 'pointer')
      .style('pointer-events', 'all')
      .on('mouseover', function (event, d) {
        setSelectedGene(null); // Clear selection when hovering a new gene
        setHoveredGene(d);

        // Highlight associated arrow
        detailSvg.selectAll('.gene-plus-arrow')
          .filter(g => g === d)
          .attr('stroke-width', 10)
          .attr('opacity', 1);
      })
      .on('mouseout', function (event, d) {
        setHoveredGene(null);

        // Remove highlight
        detailSvg.selectAll('.gene-plus-arrow')
          .attr('stroke-width', 8)
          .attr('opacity', 0.75);
      })
      .on('click', function (event, d) {
        event.stopPropagation();
        setSelectedGene(d);
      });

    detailSvg.selectAll('.gene-minus-hitbox')
      .data(minusGenes)
      .enter()
      .append('rect')
      .attr('class', 'gene-minus-hitbox')
      .attr('x', d => Math.max(margin.left, xDetail(d.start) - 5))
      .attr('y', 74) // Increased from 62 to add more space
      .attr('width', d => Math.max(10, xDetail(d.end) - xDetail(d.start) + 10))
      .attr('height', 20)
      .attr('fill', 'transparent')
      .attr('cursor', 'pointer')
      .style('pointer-events', 'all')
      .on('mouseover', function (event, d) {
        setSelectedGene(null); // Clear selection when hovering a new gene
        setHoveredGene(d);

        // Highlight associated arrow
        detailSvg.selectAll('.gene-minus-arrow')
          .filter(g => g === d)
          .attr('stroke-width', 10)
          .attr('opacity', 1);
      })
      .on('mouseout', function (event, d) {
        setHoveredGene(null);

        // Remove highlight
        detailSvg.selectAll('.gene-minus-arrow')
          .attr('stroke-width', 8)
          .attr('opacity', 0.75);
      })
      .on('click', function (event, d) {
        event.stopPropagation();
        setSelectedGene(d);
      });

    // Gene labels for each strand
    detailSvg.selectAll('.gene-label-plus')
      .data(plusGenes)
      .enter()
      .append('text')
      .attr('class', 'gene-label-plus')
      .attr('x', d => xDetail((d.start + d.end) / 2))
      .attr('y', 69) // Changed to position better with new spacing
      .attr('fill', '#333')
      .attr('font-size', 13)
      .attr('text-anchor', 'middle')
      .attr('alignment-baseline', 'hanging')
      .attr('clip-path', 'url(#detail-clip)')
      .text((d, i) => xDetail(d.end) - xDetail(d.start) > 20 ? d.id : '');
    detailSvg.selectAll('.gene-label-minus')
      .data(minusGenes)
      .enter()
      .append('text')
      .attr('class', 'gene-label-minus')
      .attr('x', d => xDetail((d.start + d.end) / 2))
      .attr('y', 99) // Changed from 85 to position better with new spacing
      .attr('fill', '#333')
      .attr('font-size', 13)
      .attr('text-anchor', 'middle')
      .attr('alignment-baseline', 'hanging')
      .attr('clip-path', 'url(#detail-clip)')
      .text((d, i) => xDetail(d.end) - xDetail(d.start) > 20 ? d.id : '');

    // --- DNA LETTERS (when zoomed in enough) ---
    const bpPerPixel = (zoomRegion[1] - zoomRegion[0]) / (availableWidth - margin.left - margin.right);
    if (bpPerPixel <= 0.2 && realSequence.length > 0) { // 1bp per 5 pixels
      // Only show letters if zoomed enough (1bp per 5 pixel or better)
      const start = Math.max(0, Math.floor(zoomRegion[0]));
      const end = Math.min(realSequence.length, Math.ceil(zoomRegion[1]));
      for (let i = start; i < end; ++i) {
        const base = realSequence[i] || '';
        detailSvg.append('text')
          .attr('x', xDetail(i + 0.5))
          .attr('y', 38)
          .attr('text-anchor', 'middle')
          .attr('font-size', 16)
          .attr('font-family', 'monospace')
          .attr('fill', baseColors[base] || '#222')
          .attr('pointer-events', 'none')
          .text(base);
      }
    }
    // --- SCALES for + strand (detail bar only, above the bar) ---
    const tickCount = 10;
    const ticks = xDetail.ticks(tickCount).filter(t => t >= zoomRegion[0] && t <= zoomRegion[1]);

    // Create a background for the scale area for brushing
    detailSvg.append('rect')
      .attr('class', 'scale-background')
      .attr('x', margin.left)
      .attr('y', 0)  // Expanded hitbox - start from the top
      .attr('width', availableWidth - margin.left - margin.right)
      .attr('height', 22)  // Taller hitbox to make selection easier
      .attr('fill', 'transparent');

    // Major ticks with labels
    detailSvg.selectAll('.scale-plus')
      .data(ticks)
      .enter()
      .append('line')
      .attr('class', 'scale-plus')
      .attr('x1', d => xDetail(d))
      .attr('x2', d => xDetail(d))
      .attr('y1', 16)
      .attr('y2', 20)
      .attr('stroke', '#555')
      .attr('stroke-width', 1.5);
    detailSvg.selectAll('.scale-plus-label')
      .data(ticks)
      .enter()
      .append('text')
      .attr('class', 'scale-plus-label')
      .attr('x', d => xDetail(d))
      .attr('y', 13)  // Moved up to accommodate larger ticks
      .attr('text-anchor', 'middle')
      .attr('font-size', 11)
      .attr('fill', '#555')
      .text(d => numberWithCommas(Math.round(d)));

    // --- BRUSH SELECTION FOR SCALE ---
    const scaleBrush = d3.brushX()
      .extent([[margin.left, 0], [availableWidth - margin.right, 22]]) // Expanded brush area
      .on('start', function (event) {
        if (!event.sourceEvent) return;
        // Prevent event propagation to avoid conflicts with chromosome drag
        if (event.sourceEvent) event.sourceEvent.stopPropagation();
      })
      .on('end', function (event) {
        // Skip if no selection or programmatic event
        if (!event.selection || !event.sourceEvent) return;

        // Prevent event propagation to avoid conflicts with chromosome drag
        if (event.sourceEvent) event.sourceEvent.stopPropagation();

        const [x0, x1] = event.selection;

        // Only process if it's a real selection (not just a click)
        if (Math.abs(x1 - x0) > 5) {
          // Convert pixels to base positions
          const newStart = xDetail.invert(x0);
          const newEnd = xDetail.invert(x1);

          // Update zoom region
          setZoomRegion([newStart, newEnd]);

          // Clear the brush
          d3.select(this).call(scaleBrush.move, null);
        }
      });

    // Add brush to the scale area
    const scaleBrushG = detailSvg.append('g')
      .attr('class', 'brush scale-brush')
      .call(scaleBrush);

    // Style the brush selection
    scaleBrushG.selectAll('.selection')
      .attr('fill', 'rgba(0, 100, 255, 0.15)')
      .attr('stroke', 'rgba(0, 100, 255, 0.8)')
      .attr('stroke-width', 1);

    // Style the brush handles
    scaleBrushG.selectAll('.handle')
      .attr('fill', 'rgba(0, 100, 255, 0.3)')
      .attr('stroke', 'rgba(0, 100, 255, 0.8)')
      .attr('stroke-width', 1);

    // Add 4 intermediate ticks between major ticks
    if (ticks.length >= 2) {
      const intermediateTicks = [];
      for (let i = 0; i < ticks.length - 1; i++) {
        const start = ticks[i];
        const end = ticks[i + 1];
        const step = (end - start) / 5;  // 5 segments = 4 intermediate ticks

        // Add 4 intermediate ticks
        for (let j = 1; j <= 4; j++) {
          intermediateTicks.push(start + step * j);
        }
      }

      detailSvg.selectAll('.scale-plus-intermediate')
        .data(intermediateTicks)
        .enter()
        .append('line')
        .attr('class', 'scale-plus-intermediate')
        .attr('x1', d => xDetail(d))
        .attr('x2', d => xDetail(d))
        .attr('y1', 17)  // Start higher for taller ticks, but less tall than major ticks
        .attr('y2', 20)  // Keep the same endpoint
        .attr('stroke', '#888')
        .attr('stroke-width', 0.8);  // Slightly thicker but still thinner than major ticks
    }

    // --- PANNING ON CHROMOSOME ---
    // Add drag behavior to chromosome bar for panning
    const dragChromosome = d3.drag()
      .on('start', function (event) {
        d3.select(this).attr('cursor', 'grabbing');
        // Store initial position to calculate delta
        d3.select(this).attr('data-start-x', event.x);
        d3.select(this).attr('data-start-zoom', JSON.stringify(zoomRegion));
      })
      .on('drag', function (event) {
        // Get the starting position and calculate shift
        const startX = parseFloat(d3.select(this).attr('data-start-x') || event.x);
        const startZoom = JSON.parse(d3.select(this).attr('data-start-zoom') || JSON.stringify(zoomRegion));

        // Total delta X from start of drag
        const deltaX = event.x - startX;

        // Calculate how far to move in chromosome coordinates
        const bpPerPixel = (startZoom[1] - startZoom[0]) / (availableWidth - margin.left - margin.right);
        const bpShift = deltaX * bpPerPixel;

        // New start and end positions, shifted from the original position
        let newStart = startZoom[0] - bpShift;
        let newEnd = startZoom[1] - bpShift;

        // Keep within chromosome bounds
        if (newStart < 0) {
          newEnd += (0 - newStart);
          newStart = 0;
        }
        if (newEnd > realChromosome.length) {
          newStart -= (newEnd - realChromosome.length);
          newEnd = realChromosome.length;
        }

        // Update the zoom region
        setZoomRegion([newStart, newEnd]);
      })
      .on('end', function () {
        d3.select(this).attr('cursor', 'grab');
        // Clean up stored data
        d3.select(this).attr('data-start-x', null);
        d3.select(this).attr('data-start-zoom', null);
      });

    // Add draggable behavior to chromosome bar with improved pointer events
    detailSvg.select('.chr-bar')
      .attr('cursor', 'grab')
      .style('pointer-events', 'all') // Ensure pointer events are enabled
      .call(dragChromosome);

    // --- Tooltip for genes in detail view ---
    detailSvg.selectAll('.gene-plus-arrow, .gene-minus-arrow')
      .on('mouseover', function (event, d) {
        setSelectedGene(null); // Clear selection when hovering a new gene
        setHoveredGene(d);
      })
      .on('mouseout', function () {
        setHoveredGene(null);
      });
    // Tooltip for genes in overview bar
    overviewSvg.selectAll('.gene')
      .on('mouseover', function (event, d) {
        setSelectedGene(null); // Clear selection when hovering a new gene
        setHoveredGene(d);
      })
      .on('mouseout', function () {
        setHoveredGene(null);
      })
      .on('click', function (event, d) {
        event.stopPropagation();
        setSelectedGene(d);
      });

    // Remove old tooltip div if any
    d3.selectAll('.genome-tooltip').remove();

    // Add click handler to clear selected gene when clicking on background
    detailSvg.append('rect')
      .attr('x', 0)
      .attr('y', 0)
      .attr('width', availableWidth)
      .attr('height', detailHeight + 40)
      .attr('fill', 'transparent')
      .style('pointer-events', 'all')
      .lower() // Send to back so it doesn't interfere with other elements
      .on('click', function () {
        setSelectedGene(null);
      });

    overviewSvg.append('rect')
      .attr('x', 0)
      .attr('y', 0)
      .attr('width', availableWidth)
      .attr('height', overviewHeight)
      .attr('fill', 'transparent')
      .style('pointer-events', 'all')
      .lower() // Send to back so it doesn't interfere with other elements
      .on('click', function () {
        setSelectedGene(null);
      });
  }, [zoomRegion]);

  // --- Top Info Bar ---
  const geneCount = realChromosome.genes.length;
  const regionStart = Math.round(zoomRegion[0]);
  const regionEnd = Math.round(zoomRegion[1]);
  const regionBp = regionEnd - regionStart;

  // --- Zoom Bar Tool ---
  const minZoom = 1;
  const width = window.innerWidth;
  const margin = { left: 60, right: 60 };
  const visiblePixels = width - margin.left - margin.right;
  const minBpWindow = visiblePixels / 20;
  const maxZoom = realChromosome.length / minBpWindow;
  // Use log10 scale for zoom slider
  const minZoomLog = Math.log10(minZoom);
  const maxZoomLog = Math.log10(maxZoom);
  const currentZoom = Math.round(realChromosome.length / (zoomRegion[1] - zoomRegion[0]));
  const currentZoomLog = Math.log10(currentZoom);

  function handleZoomBarChange(e) {
    // Get log10 value, exponentiate to get real zoom
    const logZoom = Number(e.target.value);
    const zoom = Math.pow(10, logZoom);
    const center = (zoomRegion[0] + zoomRegion[1]) / 2;
    const regionSize = realChromosome.length / zoom;
    let newStart = Math.max(0, Math.round(center - regionSize / 2));
    let newEnd = Math.min(realChromosome.length, Math.round(center + regionSize / 2));
    // Clamp if out of bounds
    if (newStart < 0) {
      newEnd += (0 - newStart);
      newStart = 0;
    }
    if (newEnd > realChromosome.length) {
      newStart -= (newEnd - realChromosome.length);
      newEnd = realChromosome.length;
    }
    setZoomRegion([newStart, newEnd]);
  }

  function handleResetView() {
    setZoomRegion([0, realChromosome.length]);
    if (zoomRef.current) {
      d3.select(detailRef.current).transition().duration(300).call(zoomRef.current.transform, d3.zoomIdentity);
    }
  }

  useEffect(() => {
    // Only reset if genes are loaded and zoomRef is initialized
    if (genes && genes.length > 0 && zoomRef.current) {
      setZoomRegion([0, realChromosome.length]);
      d3.select(detailRef.current).transition().duration(300).call(zoomRef.current.transform, d3.zoomIdentity);
    }
    // eslint-disable-next-line
  }, [genes]);

  return (
    <div style={{ position: 'relative', width: '100vw', height: '100vh', overflow: 'hidden', margin: 0, padding: 0, background: '#f0f4fa', display: 'flex', flexDirection: 'column' }}>
      {/* Top section: Info bar + Genome browser, visually carded */}
      <div style={{
        width: 'calc(100% - 48px)',
        height: '320px',
        minHeight: 260,
        margin: '24px auto 12px auto',
        background: '#fff',
        borderRadius: 18,
        boxShadow: '0 2px 12px rgba(0,0,0,0.06)',
        zIndex: 1,
        display: 'flex',
        flexDirection: 'column'
      }}>
        {/* Info bar - larger height */}
        <div style={{
          width: '100%',
          background: 'transparent',
          borderBottom: '1px solid #e1e6ee',
          padding: '14px 28px',
          fontSize: 18,
          fontWeight: 600,
          display: 'flex',
          alignItems: 'center',
          gap: 32,
          letterSpacing: '0.01em',
          position: 'sticky',
          top: 0,
          zIndex: 10,
          minHeight: 50,
          borderTopLeftRadius: 18,
          borderTopRightRadius: 18
        }}>
          <span>Chr: <b>{realChromosome.name}</b></span>
          <span>Length: <b>{numberWithCommas(realChromosome.length)} bp</b></span>
          <span>Genes: <b>{geneCount}</b></span>
          {/* --- ZOOM BAR TOOL --- */}
          <span style={{ display: 'flex', alignItems: 'center', gap: 8, minWidth: 200 }}>
            <label htmlFor="zoom-bar" style={{ fontSize: 16 }}>Zoom:</label>
            <input
              id="zoom-bar"
              type="range"
              min={minZoomLog}
              max={maxZoomLog}
              step={0.01}
              value={currentZoomLog}
              onChange={handleZoomBarChange}
              style={{ width: 120 }}
            />
            <span style={{ fontSize: 15 }}>{currentZoom}x</span>
          </span>
          {/* --- RESET VIEW BUTTON --- */}
          <button
            onClick={handleResetView}
            style={{
              marginLeft: 0,
              fontSize: 15,
              padding: '5px 14px',
              border: '1px solid #bbb',
              borderRadius: 7,
              background: '#f8f8fa',
              cursor: 'pointer',
              transition: 'background 0.2s',
              fontWeight: 600
            }}
          >Reset View</button>
          {/* --- VIEW RANGE INFO --- */}
          <span style={{
            fontSize: 16,
            color: '#444',
            marginLeft: 0,
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis'
          }}>
            View: {numberWithCommas(regionStart)} - {numberWithCommas(regionEnd)} bp ({numberWithCommas(regionBp)} bp)
          </span>
        </div>
        {/* Genome SVGs */}
        <div style={{ width: '100%', height: 'calc(100% - 64px)', background: '#fff', borderBottomLeftRadius: 18, borderBottomRightRadius: 18 }}>
          <svg ref={overviewRef} style={{ display: 'block', width: '100%' }} />
          <svg ref={detailRef} style={{ display: 'block', width: '100%' }} />
        </div>
      </div>
      {/* Bottom section: Tooltip (left) + Chatbot (right) visually carded */}
      <div style={{ display: 'flex', flex: 1, minHeight: 0, width: '100%', background: 'transparent', position: 'relative', gap: 24, padding: '0 24px 24px 24px', boxSizing: 'border-box' }}>
        {/* Tooltip area (left) */}
        <div style={{ width: '50%', minWidth: 300, height: '100%', background: '#fff', borderRadius: 18, boxShadow: '0 2px 12px rgba(0,0,0,0.06)', boxSizing: 'border-box', padding: '28px 30px', fontSize: 16, color: '#222', display: 'flex', flexDirection: 'column' }}>
          <div style={{ fontWeight: 500, marginBottom: 8 }}>Tooltip for when we select an element (currently, only genes)</div>
          {(selectedGene || hoveredGene) ? (
            <div style={{ fontSize: 18, marginTop: 16, lineHeight: 1.7 }}>
              <div><b>ID:</b> {(selectedGene || hoveredGene).id}</div>
              <div><b>Start:</b> {numberWithCommas((selectedGene || hoveredGene).start)}</div>
              <div><b>End:</b> {numberWithCommas((selectedGene || hoveredGene).end)}</div>
              <div><b>Strand:</b> {(selectedGene || hoveredGene).strand}</div>
              <br />
              <div style={{ width: '50%', margin: '0 auto' }}><b>Attributes:</b> <ul style={{ margin: 0, paddingLeft: 16, textAlign: 'left' }}>
                {Object.entries((selectedGene || hoveredGene).attributes).map(([key, value]) => (
                  <li key={key}><b>{key}:</b> {value}</li>
                ))}
              </ul></div>
              {selectedGene && (
                <div style={{ marginTop: 8, fontSize: 12, color: '#666' }}>
                  (Gene is selected. Click elsewhere to deselect.)
                </div>
              )}
            </div>
          ) : (
            <div style={{ color: '#888', marginTop: 16 }}>Hover over or click a gene to see its details here.</div>
          )}
        </div>
        {/* Chatbot area (right) */}
        <div style={{ width: '50%', minWidth: 300, height: '100%', background: '#fff', borderRadius: 18, boxShadow: '0 2px 12px rgba(0,0,0,0.06)', boxSizing: 'border-box', padding: '28px 30px', display: 'flex', flexDirection: 'column' }}>
          <div style={{ fontWeight: 500, marginBottom: 8, fontSize: 22, letterSpacing: 0.5 }}>ChatBot</div>
          {/* Chat messages area */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '8px 0', display: 'flex', flexDirection: 'column', gap: 14 }}>
            {/* Placeholder for messages */}
            <div style={{ alignSelf: 'flex-start', background: '#f0f6ff', borderRadius: 8, padding: '12px 18px', fontSize: 16, color: '#222', maxWidth: '80%' }}>
              Hello! I can help answer questions about the genome you're viewing.
            </div>
            <div style={{ color: '#aaa', fontSize: 14, fontStyle: 'italic', alignSelf: 'center', margin: '10px 0' }}>
              Messages will appear here.
            </div>
          </div>
          {/* Input area */}
          <form style={{ display: 'flex', gap: 8, marginTop: 12 }} onSubmit={e => e.preventDefault()}>
            <input
              type="text"
              placeholder="Type a message..."
              style={{
                flex: 1,
                padding: '12px 16px',
                borderRadius: 20,
                border: '1px solid #ddd',
                fontSize: 16,
                background: '#f8f8fa',
                outline: 'none'
              }}
              disabled
            />
            <button
              type="submit"
              style={{
                background: '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '50%',
                width: 40,
                height: 40,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 20,
                cursor: 'not-allowed',
                opacity: 0.7
              }}
              disabled
            >→</button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default GenomeBrowser;
