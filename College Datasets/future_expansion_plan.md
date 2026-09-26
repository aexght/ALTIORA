# Future Expansion Plan

## Scaling Strategy

### Phase 1 (Current)
- **Scale**: 120 colleges, core schema established.
- **Focus**: Validate the ER model, establish controlled vocabularies, and ensure the basic end-to-end data pipeline functions for the ML Recommendation Engine.
- **Schema/Data Changes**: No schema changes needed. The foundation is set with strict normal forms and controlled vocabularies.

### Phase 2 (Target: 150 → 500 Colleges)
- **Scope**: Expand geography to add Rajasthan, MP, West Bengal, Odisha, Punjab, Haryana, Bihar, Jharkhand, Assam, and Goa. Deepen coverage in existing states.
- **Schema Changes**: None required. The highly normalized structure seamlessly absorbs new locations and domains.
- **Data Changes**: Aggressively fill `Unknown` values for NAAC, NIRF, Official Website, and Hostel availability. Increase course mapping density for existing colleges.
- **Estimated Effort**: Moderate. Requires distributed scraping or dedicated data entry for the new states.

### Phase 3 (Target: 500 → 1000+ Colleges)
- **Scope**: Full national coverage, encompassing all States and Union Territories. Expand significantly into Tier-2 and Tier-3 cities and diverse multi-disciplinary colleges.
- **Schema Changes**: None.
- **Data Changes**: Massive ingestion of state-level university affiliates and private institutions.
- **Estimated Effort**: High. Will rely heavily on automated data pipelines and structured verification workflows.

## Data Collection Strategy
- **Batch-by-Batch Verification**: Data will be ingested in batches by state or specific domains (e.g., all Medical colleges in a state first).
- **NIRF-First Approach**: Top-ranked and most-searched colleges are prioritized for data completeness to ensure the recommendation engine provides immediate value for high-intent queries.

## Automation Opportunities
- **AICTE API**: Utilize AICTE's open data initiatives to automatically fetch approved engineering and management institution metadata and intake capacities.
- **NIRF Scraping**: Automate extraction from NIRF PDF reports, noting caveats around OCR errors and varied formatting across different years.
- **NAAC Assessment Reports**: Programmatically scrape NAAC accredited institution lists to update the `NAAC_Grade` fields automatically.

## Modular Architecture Benefits
- **Fee Database**: Because `fee_database.csv` is completely decoupled, annual tuition hikes can be integrated via batch updates without disrupting the college metadata or core mappings.
- **Image Download Manifest**: The `image_download_manifest.csv` enables async bulk media asset management. A background worker can consume this manifest to download, resize, and host images on a CDN without blocking the data team.

## Integration Points
- **Flask Backend**: Exposes the normalized datasets via RESTful APIs. It will query the CSVs (or a loaded SQL replica) to serve filtered JSON responses based on user constraints (budget, state, NAAC grade).
- **React Frontend**: Consumes the API to render dynamic dropdowns (States, Career Domains) based on the exact controlled vocabulary. The decoupled images are loaded directly via the URLs generated from the manifest pipeline.
