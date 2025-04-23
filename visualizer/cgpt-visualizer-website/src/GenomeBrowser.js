import React, { useRef, useEffect, useState } from 'react';
import * as d3 from 'd3';

const mockChromosome = {
  name: 'chr1',
  length: 25000000, // demo: 25 million bp for visible genes
  genes: [
    { name: 'GENE1', start: 1000000, end: 1010000, strand: '+', color: '#4F81BD' },
    { name: 'GENE2', start: 5000000, end: 5015000, strand: '-', color: '#C0504D' },
    { name: 'GENE3', start: 20000000, end: 20005000, strand: '+', color: '#9BBB59' },
  ]
};

function numberWithCommas(x) {
  return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

function GenomeBrowser() {
  const overviewRef = useRef();
  const detailRef = useRef();
  const zoomRef = useRef();
  const [zoomRegion, setZoomRegion] = useState([0, mockChromosome.length]);

  // --- D3 Zoom Setup: Only once on mount ---
  useEffect(() => {
    const width = window.innerWidth;
    const detailHeight = 80;
    const margin = { left: 60, right: 60 };

    const zoom = d3.zoom()
      .scaleExtent([1, mockChromosome.length / 100000])
      .translateExtent([[margin.left, 0], [width - margin.right, detailHeight]])
      .extent([[margin.left, 0], [width - margin.right, detailHeight]])
      .on('zoom', (event) => {
        const t = event.transform;
        const x = d3.scaleLinear().domain([0, mockChromosome.length]).range([margin.left, width - margin.right]);
        const newDomain = t.rescaleX(x).domain();
        // Clamp to chromosome
        let newRegion = [
          Math.max(0, newDomain[0]),
          Math.min(mockChromosome.length, newDomain[1])
        ];
        // If zoomed out to the full chromosome (or beyond), snap to full
        if (newRegion[0] <= 0 + 1 && newRegion[1] >= mockChromosome.length - 1) {
          newRegion = [0, mockChromosome.length];
        }
        // Only update if region changed
        if (
          Math.abs(newRegion[0] - zoomRegion[0]) > 1 ||
          Math.abs(newRegion[1] - zoomRegion[1]) > 1
        ) {
          setZoomRegion(newRegion);
        }
      });
    d3.select(detailRef.current).call(zoom);
    zoomRef.current = zoom;
    // Initial transform (fit whole chromosome)
    d3.select(detailRef.current).call(zoom.transform, d3.zoomIdentity);
    // Prevent default D3 double-click zoom-in and use our own reset
    d3.select(detailRef.current).on('dblclick.zoom', null);
    d3.select(detailRef.current).on('dblclick.reset', () => {
      d3.select(detailRef.current).transition().duration(300).call(zoom.transform, d3.zoomIdentity);
      setZoomRegion([0, mockChromosome.length]);
    });
    // eslint-disable-next-line
  }, []);

  // --- Draw both SVGs whenever zoomRegion changes ---
  useEffect(() => {
    const width = window.innerWidth;
    const overviewHeight = 80;
    const detailHeight = 100;
    const margin = { left: 60, right: 60 };
    // -- OVERVIEW BAR --
    d3.select(overviewRef.current).selectAll('*').remove();
    const overviewSvg = d3.select(overviewRef.current)
      .attr('width', width)
      .attr('height', overviewHeight)
      .style('background', '#f8f8fa');
    const xOverview = d3.scaleLinear()
      .domain([0, mockChromosome.length])
      .range([margin.left, width - margin.right]);
    // Chromosome bar (move lower)
    const overviewBarY = 32; // was 12, now lower for scale visibility
    overviewSvg.append('rect')
      .attr('x', margin.left)
      .attr('y', overviewBarY)
      .attr('width', width - margin.left - margin.right)
      .attr('height', 16)
      .attr('rx', 10)
      .attr('fill', '#cccccc');
    // Genes
    overviewSvg.selectAll('.gene')
      .data(mockChromosome.genes)
      .enter()
      .append('rect')
      .attr('class', 'gene')
      .attr('x', d => xOverview(d.start))
      .attr('y', overviewBarY + 1)
      .attr('width', d => Math.max(1, xOverview(d.end) - xOverview(d.start)))
      .attr('height', 14)
      .attr('fill', d => d.color)
      .attr('rx', 5);
    // Red rectangle for zoom region
    const isFullView = zoomRegion[0] <= 0 + 1 && zoomRegion[1] >= mockChromosome.length - 1;
    overviewSvg.append('rect')
      .attr('class', 'zoom-rect')
      .attr('x', isFullView ? margin.left : xOverview(zoomRegion[0]))
      .attr('y', overviewBarY - 5)
      .attr('width', isFullView ? (width - margin.left - margin.right) : (xOverview(zoomRegion[1]) - xOverview(zoomRegion[0])))
      .attr('height', 26)
      .attr('fill', 'none')
      .attr('stroke', 'red')
      .attr('stroke-width', 2);
    // --- SCALES for + strand (overview bar, above the bar) ---
    const overviewTicks = xOverview.ticks(10).filter(t => t >= 0 && t <= mockChromosome.length);
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
      .attr('width', width)
      .attr('height', detailHeight + 40)
      .style('background', '#fff');
    // Scales
    const xDetail = d3.scaleLinear()
      .domain(zoomRegion)
      .range([margin.left, width - margin.right]);
    // Add a clipPath for the chromosome bar area
    detailSvg.append('clipPath')
      .attr('id', 'detail-clip')
      .append('rect')
      .attr('x', margin.left)
      .attr('y', 20)
      .attr('width', width - margin.left - margin.right)
      .attr('height', 24);
    // Chromosome bar
    // Remove rounded corners except at chromosome ends
    const isAtChromStart = Math.abs(zoomRegion[0] - 0) < 1;
    const isAtChromEnd = Math.abs(zoomRegion[1] - mockChromosome.length) < 1;
    let rxLeft = isAtChromStart ? 10 : 0;
    let rxRight = isAtChromEnd ? 10 : 0;
    // SVG only supports one rx, so we use a path for custom corners
    if (rxLeft !== rxRight) {
      // Draw as path for mixed corners
      const barY = 20;
      const barH = 24;
      const barX = margin.left;
      const barW = width - margin.left - margin.right;
      let d = '';
      d += `M${barX + rxLeft},${barY}`;
      d += `H${barX + barW - rxRight}`;
      if (rxRight) {
        d += `A${rxRight},${rxRight} 0 0 1 ${barX + barW},${barY + rxRight}`;
        d += `V${barY + barH - rxRight}`;
        d += `A${rxRight},${rxRight} 0 0 1 ${barX + barW - rxRight},${barY + barH}`;
      } else {
        d += `V${barY + barH}`;
      }
      d += `H${barX + rxLeft}`;
      if (rxLeft) {
        d += `A${rxLeft},${rxLeft} 0 0 1 ${barX},${barY + barH - rxLeft}`;
        d += `V${barY + rxLeft}`;
        d += `A${rxLeft},${rxLeft} 0 0 1 ${barX + rxLeft},${barY}`;
      } else {
        d += `V${barY}`;
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
        .attr('y', 20)
        .attr('width', width - margin.left - margin.right)
        .attr('height', 24)
        .attr('rx', rxLeft)
        .attr('fill', '#cccccc');
    }
    // Genes (clipped)
    detailSvg.selectAll('.gene')
      .data(mockChromosome.genes)
      .enter()
      .append('rect')
      .attr('class', 'gene')
      .attr('x', d => xDetail(d.start))
      .attr('y', 24)
      .attr('width', d => Math.max(1, xDetail(d.end) - xDetail(d.start)))
      .attr('height', 16)
      .attr('fill', d => d.color)
      .attr('rx', 5)
      .attr('clip-path', 'url(#detail-clip)')
      .on('mouseover', function (event, d) {
        d3.select(this).attr('stroke', 'black').attr('stroke-width', 2);
        tooltip.style('display', 'block')
          .html(`<b>${d.name}</b><br/>${numberWithCommas(d.start)} - ${numberWithCommas(d.end)}<br/>Strand: ${d.strand}`)
          .style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY - 28) + 'px');
      })
      .on('mouseout', function () {
        d3.select(this).attr('stroke', null);
        tooltip.style('display', 'none');
      });
    // Gene labels under the bar (clipped)
    detailSvg.selectAll('.gene-label')
      .data(mockChromosome.genes)
      .enter()
      .append('text')
      .attr('class', 'gene-label')
      .attr('x', d => xDetail((d.start + d.end) / 2))
      .attr('y', 56)
      .attr('fill', '#333')
      .attr('font-size', 13)
      .attr('text-anchor', 'middle')
      .attr('alignment-baseline', 'hanging')
      .attr('clip-path', 'url(#detail-clip)')
      .text(d => xDetail(d.end) - xDetail(d.start) > 20 ? d.name : '');
    // --- SCALES for + strand (detail bar only, above the bar) ---
    const tickCount = 10;
    const ticks = xDetail.ticks(tickCount).filter(t => t >= zoomRegion[0] && t <= zoomRegion[1]);
    detailSvg.selectAll('.scale-plus')
      .data(ticks)
      .enter()
      .append('line')
      .attr('class', 'scale-plus')
      .attr('x1', d => xDetail(d))
      .attr('x2', d => xDetail(d))
      .attr('y1', 18)
      .attr('y2', 20)
      .attr('stroke', '#555')
      .attr('stroke-width', 1);
    detailSvg.selectAll('.scale-plus-label')
      .data(ticks)
      .enter()
      .append('text')
      .attr('class', 'scale-plus-label')
      .attr('x', d => xDetail(d))
      .attr('y', 14)
      .attr('text-anchor', 'middle')
      .attr('font-size', 11)
      .attr('fill', '#555')
      .text(d => numberWithCommas(Math.round(d)));
    // Tooltip
    const tooltip = d3.select('body').append('div')
      .attr('class', 'genome-tooltip')
      .style('position', 'absolute')
      .style('background', '#fff')
      .style('border', '1px solid #ccc')
      .style('padding', '6px 12px')
      .style('border-radius', '4px')
      .style('pointer-events', 'none')
      .style('display', 'none')
      .style('font-size', '14px');
    return () => {
      tooltip.remove();
    };
  }, [zoomRegion]);

  // --- Top Info Bar ---
  const geneCount = mockChromosome.genes.length;
  const regionStart = Math.round(zoomRegion[0]);
  const regionEnd = Math.round(zoomRegion[1]);
  const regionBp = regionEnd - regionStart;

  // --- Zoom Bar Tool ---
  // Slider min: 1x (full view), max: 100x zoom (arbitrary, can adjust)
  const minZoom = 1;
  const maxZoom = 100;
  const fullRegion = [0, mockChromosome.length];
  const currentZoom = Math.round(mockChromosome.length / (zoomRegion[1] - zoomRegion[0]));

  function handleZoomBarChange(e) {
    const zoom = Number(e.target.value);
    const center = (zoomRegion[0] + zoomRegion[1]) / 2;
    const regionSize = mockChromosome.length / zoom;
    let newStart = Math.max(0, Math.round(center - regionSize / 2));
    let newEnd = Math.min(mockChromosome.length, Math.round(center + regionSize / 2));
    // Clamp if out of bounds
    if (newStart < 0) {
      newEnd -= newStart;
      newStart = 0;
    }
    if (newEnd > mockChromosome.length) {
      newStart -= (newEnd - mockChromosome.length);
      newEnd = mockChromosome.length;
    }
    setZoomRegion([newStart, newEnd]);
  }

  function handleResetView() {
    setZoomRegion([0, mockChromosome.length]);
    if (zoomRef.current) {
      d3.select(detailRef.current).transition().duration(300).call(zoomRef.current.transform, d3.zoomIdentity);
    }
  }

  return (
    <div style={{ width: '100vw', height: '100vh', overflow: 'hidden', margin: 0, padding: 0, background: '#f8f8fa' }}>
      <div style={{
        width: '100vw',
        background: '#f0f4fa',
        borderBottom: '1px solid #d0d6e0',
        padding: '10px 40px 8px 40px',
        fontSize: 18,
        fontWeight: 500,
        display: 'flex',
        alignItems: 'center',
        gap: 40,
        letterSpacing: '0.01em',
        position: 'sticky',
        top: 0,
        zIndex: 10
      }}>
        <span>Chr: <b>{mockChromosome.name}</b></span>
        <span>Length: <b>{numberWithCommas(mockChromosome.length)} bp</b></span>
        <span>Genes: <b>{geneCount}</b></span>
        {/* --- ZOOM BAR TOOL --- */}
        <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <label htmlFor="zoom-bar" style={{ fontSize: 15 }}>Zoom:</label>
          <input
            id="zoom-bar"
            type="range"
            min={minZoom}
            max={maxZoom}
            value={currentZoom}
            onChange={handleZoomBarChange}
            style={{ width: 120 }}
          />
          <span style={{ fontSize: 14 }}>{currentZoom}x</span>
        </span>
        {/* --- RESET VIEW BUTTON --- */}
        <button
          onClick={handleResetView}
          style={{
            marginLeft: 12,
            fontSize: 14,
            padding: '4px 14px',
            border: '1px solid #bbb',
            borderRadius: 6,
            background: '#f8f8fa',
            cursor: 'pointer',
            transition: 'background 0.2s',
            fontWeight: 500
          }}
        >Reset View</button>
        {/* --- VIEW RANGE INFO (last element, left aligned) --- */}
        <span style={{ fontSize: 16, color: '#444' }}>
          View: {numberWithCommas(regionStart)} - {numberWithCommas(regionEnd)} bp ({numberWithCommas(regionBp)} bp)
        </span>
      </div>
      <svg ref={overviewRef} style={{ display: 'block' }}></svg>
      <svg ref={detailRef} style={{ display: 'block' }}></svg>
    </div>
  );
}

export default GenomeBrowser;
