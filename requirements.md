# Requirements Specification

## Project Overview

**Talent-Seekr** is an automated AI founder discovery system designed to identify early-stage AI talent in Australia through multi-platform signal detection, replacing manual LinkedIn scouting with intelligent talent pipeline automation.

## Business Requirements

### Core Objective
- **Primary Goal**: Automate discovery of Australia-based early-stage AI founders
- **Current Problem**: VC manually scouts AI founders on LinkedIn → inefficient, slow, limited reach
- **Solution**: Automated multi-platform talent scouting with intelligent scoring and workflow integration

### Target Profile Definition
**Australia-Based AI Builders** with founder intent signals:

#### Technical Founders
- Engineers, data scientists, ML/AI researchers
- Open source contributors, LLM tinkerers
- Side project builders with AI focus

#### Commercial Founders  
- Product managers with AI experience
- Operators building AI-powered tools
- Content-led growth marketers in AI space
- Individuals building MVPs or launching GTM experiments

#### Australia Connection Requirements
- **Primary Signals**: .edu.au/.com.au email domains
- **Secondary Signals**: AU organization affiliations, AU startup ecosystem ties
- **Geographic Indicators**: AU location metadata, timezone activity patterns

#### Founder Intent Signals
- **Active Building**: Shipping products, launching tools, public demos
- **Thought Leadership**: Speaking at events, writing about AI experiences
- **Community Engagement**: Sharing learnings, participating in AI discussions
- **Experimentation**: GTM experiments, user feedback collection

### Workflow Integration
**VC Team Workflow**: Discover → Cold Call → Follow-up → Decision
- **Discover**: System identifies new high-potential candidates
- **Cold Call**: Initial outreach and conversation
- **Follow-up**: Second call, usually first response from talents
- **Decision**: Potential candidate, hard reject, or later follow-up

### Success Metrics
- **Discovery Volume**: 50-100 new qualified prospects per week
- **Quality Threshold**: Score >60 for inclusion, >80 for high priority
- **Time Savings**: 80%+ reduction in manual scouting time
- **Conversion Rate**: Track from discovery to actual meetings/investments

## Technical Requirements

### Data Sources (Current Scope)
1. **GitHub** (Day 1)
   - AI repository contributors and maintainers
   - Frequent committers on ML/AI projects
   - Solo authors with AI focus

2. **Twitter/X** (Day 2)  
   - Users posting about "finetuning", "GPT", "RAG", LLMs
   - AI discussions with engagement
   - Building-in-public content

### Future Data Sources (Post-MVP)
3. **LinkedIn** - Professional AI profiles and activities
4. **Product Hunt** - AI tool launches and maker profiles
5. **Reddit/Hacker News** - "Show HN" posts, r/MachineLearning contributions
6. **Meetup/Luma** - AI event organizers and active participants
7. **Substack/Blogs** - Authors discussing AI MVPs and GTM experiments
8. **Discord Communities** - AI group participants sharing demos

### Processing Requirements
- **Batch Processing**: Weekly discovery runs (Sunday nights)
- **Real-time Updates**: Score updates and new high-priority alerts
- **Deduplication**: Merge profiles found across multiple platforms
- **Quality Filtering**: Automated threshold-based inclusion

### Scoring Requirements
- **ML-Powered Scoring**: Adaptive algorithm learning from feedback
- **Multi-Factor Analysis**: Technical depth + founder intent + commercial awareness
- **AU Connection Weighting**: Prioritize strong Australian ties
- **Platform-Specific Signals**: Custom scoring per data source

### Database Requirements
- **Primary Storage**: Notion database for team collaboration
- **Data Retention**: Indefinite storage for relationship building
- **Update Frequency**: Weekly batch updates, real-time status changes
- **Access Control**: Team-based permissions within Notion

### Integration Requirements
- **Notion API**: Primary interface for data storage and team access
- **Platform APIs**: GitHub API, Twitter scraping, future API integrations
- **Monitoring**: Pipeline health, API rate limits, error tracking
- **Configuration**: YAML-based settings for easy deployment adjustments

## Functional Requirements

### Core Pipeline Functions
1. **Data Collection**: Multi-platform scraping with rate limit management
2. **AU Filtering**: Automated detection of Australian connections
3. **Talent Scoring**: ML-based ranking with confidence indicators
4. **Deduplication**: Cross-platform profile matching and merging
5. **Quality Control**: Threshold-based filtering and manual review flags
6. **Database Sync**: Automated Notion database updates

### User Interface Requirements
- **Primary Interface**: Notion database with custom views
- **Filtering Capabilities**: By score, status, discovery date, platform source
- **Workflow Management**: Status tracking, assignment, notes, follow-up dates
- **Mobile Access**: Full functionality through Notion mobile apps

### Configuration Management
- **Plugin System**: Easy enabling/disabling of data sources
- **Scoring Tuning**: Adjustable weights for different signal types
- **AU Detection**: Customizable rules for Australian connection detection
- **Quality Thresholds**: Configurable minimum scores for inclusion

## Non-Functional Requirements

### Performance Requirements
- **Weekly Processing**: Complete discovery cycle within 8 hours
- **API Rate Limits**: Respect all platform limits with exponential backoff
- **Error Handling**: Graceful degradation when sources are unavailable
- **Scalability**: Handle 1000+ prospects per week without performance degradation

### Reliability Requirements
- **Uptime**: 99%+ availability for weekly processing
- **Data Integrity**: No duplicate entries, consistent scoring
- **Recovery**: Automatic retry for failed API calls
- **Monitoring**: Alerts for pipeline failures or quality drops

### Security Requirements
- **API Keys**: Secure storage of authentication credentials
- **Data Privacy**: Publicly available data only, no private information
- **Access Control**: Team-based access through Notion permissions
- **Audit Trail**: Track all data collection and scoring activities

### Maintainability Requirements
- **Modular Design**: Plugin architecture for easy source addition
- **Documentation**: Comprehensive setup and operation guides
- **Testing**: Automated tests for core pipeline functions
- **Monitoring**: Health checks and performance metrics

## Constraints and Assumptions

### Technical Constraints
- **API Limitations**: GitHub 5K/hour, Twitter restricted access post-2023
- **Rate Limiting**: All sources require respectful usage patterns
- **Data Freshness**: Weekly updates acceptable for business needs
- **Platform Dependencies**: Changes to platform APIs may affect data collection

### Business Constraints
- **Timeline**: 3-day MVP development window
- **Budget**: Minimal infrastructure costs preferred
- **Team**: Small development team, prefer low-maintenance solutions
- **Compliance**: Public data only, no GDPR concerns for business use

### Assumptions
- **Notion Adoption**: Team comfortable with Notion as primary interface
- **AU Market Focus**: Australian AI ecosystem remains primary target
- **Signal Stability**: Public platform activities remain predictive of founder potential
- **Manual Workflow**: Human oversight remains important for relationship building

## Success Criteria

### MVP Success (3 Days)
- [ ] GitHub + Twitter data collection working
- [ ] Basic scoring algorithm operational  
- [ ] Notion database integration functional
- [ ] 20+ qualified AU AI founders discovered

### Production Success (Ongoing)
- [ ] 50+ new prospects per week discovery rate
- [ ] 80%+ time reduction vs manual LinkedIn scouting  
- [ ] 90%+ AU connection accuracy in results
- [ ] Team adoption and workflow integration

### Long-term Success (3+ Months)
- [ ] 5+ data sources integrated and operational
- [ ] ML scoring improvement with feedback loops
- [ ] Measurable improvement in investment pipeline quality
- [ ] Expansion to other geographic markets or sectors