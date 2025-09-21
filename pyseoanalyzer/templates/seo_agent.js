class SEOAgent {
    constructor() {
        this.apiBaseUrl = `http://${window.location.hostname}:${window.location.port}/api`;
        this.currentAnalysis = null;
        this.todos = JSON.parse(localStorage.getItem('seoTodos')) || [];
        this.theme = localStorage.getItem('theme') || 'light';
        this.currentSection = 'summary';
        this.init();
    }

    init() {
        this.initTheme();
        this.bindEvents();
        this.renderTodos();
        this.updateTodoStats();
        this.initAnimations();
        this.initSectionNavigation();
        this.initUsageTracking();
        this.checkApiHealth();
    }

    initTheme() {
        if (this.theme === 'auto') {
            const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', systemTheme);
        } else {
            document.documentElement.setAttribute('data-theme', this.theme);
        }

        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (this.theme === 'auto') {
                document.documentElement.setAttribute('data-theme', e.matches ? 'dark' : 'light');
            }
        });
    }

    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        this.theme = newTheme;
        localStorage.setItem('theme', newTheme);

        const toggle = document.querySelector('.theme-toggle');
        if (toggle) {
            toggle.classList.add('bounce-in');
            setTimeout(() => toggle.classList.remove('bounce-in'), 800);
        }
    }

    initAnimations() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('.stagger-item').forEach((item, index) => {
            item.style.animationDelay = `${index * 100}ms`;
            observer.observe(item);
        });
    }

    initSectionNavigation() {
        document.querySelectorAll('.nav-item').forEach(navItem => {
            navItem.addEventListener('click', (e) => {
                e.preventDefault();
                const href = navItem.getAttribute('onclick');
                if (href && href.includes('showSection')) {
                    const section = href.match(/'([^']+)'/)[1];
                    this.showSection(section);
                }
            });
        });

        this.showSection(this.currentSection);
    }

    initUsageTracking() {
        const usageText = document.getElementById('usageText');
        if (usageText) {
            // Free to use - no restrictions
            usageText.textContent = 'Unlimited FREE analysis • No signup required';
        }
    }

    getTodayUsage() {
        const today = new Date().toDateString();
        const usage = JSON.parse(localStorage.getItem('dailyUsage') || '{}');
        return usage[today] || 0;
    }

    incrementUsage() {
        const today = new Date().toDateString();
        const usage = JSON.parse(localStorage.getItem('dailyUsage') || '{}');
        usage[today] = (usage[today] || 0) + 1;
        localStorage.setItem('dailyUsage', JSON.stringify(usage));
        this.initUsageTracking();
    }

    showSection(sectionId) {
        document.querySelectorAll('.analysis-section').forEach(section => {
            section.classList.remove('active');
        });

        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active', 'text-purple-600', 'bg-purple-50');
            item.classList.add('text-gray-700');
        });

        const targetSection = document.getElementById(sectionId);
        if (targetSection) {
            targetSection.classList.add('active');
        }

        const activeNavItem = document.querySelector(`[onclick="showSection('${sectionId}')"]`);
        if (activeNavItem) {
            activeNavItem.classList.remove('text-gray-700');
            activeNavItem.classList.add('active', 'text-purple-600', 'bg-purple-50');
        }

        this.currentSection = sectionId;
        this.initSectionContent(sectionId);
    }

    initSectionContent(sectionId) {
        switch(sectionId) {
            case 'summary':
                if (this.currentAnalysis) {
                    this.updateSummarySection(this.currentAnalysis);
                }
                break;
            case 'seo-analysis':
                if (this.currentAnalysis) {
                    this.updateSEOAnalysisSection(this.currentAnalysis);
                }
                break;
            case 'site-compliance':
                if (this.currentAnalysis) {
                    this.updateComplianceSection(this.currentAnalysis);
                }
                break;
            case 'links':
                if (this.currentAnalysis) {
                    this.updateLinksSection(this.currentAnalysis);
                }
                break;
            case 'seo-strategy':
                this.updateSEOStrategySection();
                break;
            case 'trends-analysis': // 🔥 Add trends analysis section
                this.updateTrendsAnalysisSection();
                break;
        }
    }

    showLoadingProgress(step, message, progress, stepNumber = 1) {
        const loadingTitle = document.getElementById('loadingTitle');
        const loadingMessage = document.getElementById('loadingMessage');
        const loadingProgress = document.getElementById('loadingProgress');
        const loadingStep = document.getElementById('loadingStep');
        const loadingPercent = document.getElementById('loadingPercent');
        
        // Professional loading messages with animations
        if (loadingTitle) {
            const titles = [
                '🤖 AI Brain Analyzing...',
                '🔍 Discovering SEO Secrets...',
                '⚡ Unleashing Optimization Power...',
                '🎯 Targeting Growth Opportunities...'
            ];
            loadingTitle.textContent = titles[Math.min(stepNumber - 1, titles.length - 1)] || titles[0];
            loadingTitle.style.opacity = '0';
            setTimeout(() => {
                loadingTitle.style.transition = 'opacity 0.3s ease';
                loadingTitle.style.opacity = '1';
            }, 100);
        }
        
        if (loadingMessage) {
            loadingMessage.textContent = message;
            loadingMessage.classList.add('fade-in');
        }
        
        if (loadingProgress) {
            loadingProgress.style.width = `${progress}%`;
            loadingProgress.style.transition = 'width 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
        }
        
        if (loadingStep) {
            loadingStep.textContent = step;
            loadingStep.classList.add('bounce-in');
        }
        
        if (loadingPercent) {
            loadingPercent.textContent = `${progress}%`;
            loadingPercent.style.fontWeight = '600';
            loadingPercent.style.color = progress === 100 ? '#10b981' : '#6366f1';
        }

        // Enhanced step indicators with better visual feedback
        document.querySelectorAll('.loading-step').forEach((stepEl, index) => {
            const stepIndicator = stepEl.querySelector('.status-indicator');
            if (stepIndicator) {
                stepIndicator.style.transition = 'all 0.3s ease';
                if (index + 1 < stepNumber) {
                    stepIndicator.className = 'status-indicator status-online';
                } else if (index + 1 === stepNumber) {
                    stepIndicator.className = 'status-indicator status-processing';
                    stepEl.classList.add('active');
                } else {
                    stepIndicator.className = 'status-indicator status-offline';
                    stepEl.classList.remove('active');
                }
            }
        });
        
        // Add professional pulsing effect for current step
        if (stepNumber <= 4) {
            const currentStep = document.querySelector(`.loading-step:nth-child(${stepNumber})`);
            if (currentStep) {
                currentStep.style.transform = 'scale(1.05)';
                setTimeout(() => {
                    currentStep.style.transform = 'scale(1)';
                }, 200);
            }
        }
    }

    bindEvents() {
        const analyzeBtn = document.getElementById('analyzeBtn');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.analyzeWebsite());
        }

        const urlInput = document.getElementById('urlInput');
        if (urlInput) {
            urlInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.analyzeWebsite();
                }
            });
            
            urlInput.addEventListener('input', (e) => {
                this.validateURL(e.target.value);
            });
        }

        document.getElementById('addTodoBtn')?.addEventListener('click', () => this.showAddTodoForm());
        document.getElementById('saveTodoBtn')?.addEventListener('click', () => this.saveTodo());
        document.getElementById('clearCompletedBtn')?.addEventListener('click', () => this.clearCompleted());
        
        // Sitemap generation button
        document.getElementById('generateSitemapBtn')?.addEventListener('click', () => this.generateSitemap());
        
        // Report download button
        document.getElementById('downloadReportBtn')?.addEventListener('click', () => this.downloadReport());
        
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.analyzeWebsite();
            }
        });
    }
    
    validateURL(url) {
        const urlValidation = document.getElementById('urlValidation');
        const urlError = document.getElementById('urlError');
        const analyzeBtn = document.getElementById('analyzeBtn');
        
        if (!url) {
            urlValidation?.classList.add('hidden');
            urlError?.classList.add('hidden');
            if (analyzeBtn) analyzeBtn.disabled = false;
            return;
        }
        
        try {
            const urlObj = new URL(url);
            if (urlObj.protocol === 'http:' || urlObj.protocol === 'https:') {
                urlValidation?.classList.remove('hidden');
                urlError?.classList.add('hidden');
                if (analyzeBtn) analyzeBtn.disabled = false;
            } else {
                throw new Error('Protocol not supported');
            }
        } catch (error) {
            urlValidation?.classList.add('hidden');
            if (urlError) {
                urlError.textContent = 'URL format is incorrect, please enter a complete URL';
                urlError.classList.remove('hidden');
            }
            if (analyzeBtn) analyzeBtn.disabled = true;
        }
    }

    async analyzeWebsite() {
        const urlInput = document.getElementById('urlInput');
        const url = urlInput?.value?.trim();
        
        if (!url) {
            this.showAlert('Please enter a valid website URL', 'warning');
            return;
        }

        // Usage limit removed - free to use without restrictions

        this.showLoading(true);
        
        let progressInterval = null;
        
        try {
            this.showLoadingProgress('🔍 Step 1/4: Discovering your website', 'Establishing secure connection and crawling...', 25, 1);
            
            // 启动进度条动画，让用户知道系统在运行
            let currentProgress = 25;
            let stepPhase = 1;
            const progressMessages = [
                { min: 25, max: 40, title: '🤖 AI Brain Analyzing...', message: 'Processing with SiliconFlow AI, please wait...', step: 2 },
                { min: 40, max: 55, title: '🔍 Discovering SEO Secrets...', message: 'AI is analyzing content structure and keywords...', step: 2 },
                { min: 55, max: 70, title: '⚡ Unleashing Optimization Power...', message: 'Generating personalized recommendations...', step: 3 },
                { min: 70, max: 85, title: '🔮 AI Deep Analysis...', message: 'Finalizing strategic insights, almost complete...', step: 3 },
                { min: 85, max: 98, title: '✨ Completing Analysis...', message: 'Preparing your intelligent SEO strategy...', step: 4 }
            ];
            
            progressInterval = setInterval(() => {
                if (currentProgress < 98) {
                    // 动态调整进度增长速度
                    const increment = currentProgress < 85 ? Math.random() * 1.5 + 0.5 : Math.random() * 0.8 + 0.2;
                    currentProgress += increment;
                    
                    // 找到当前进度对应的消息
                    const currentPhase = progressMessages.find(phase => 
                        currentProgress >= phase.min && currentProgress <= phase.max
                    );
                    
                    if (currentPhase) {
                        this.showLoadingProgress(
                            currentPhase.title, 
                            currentPhase.message, 
                            Math.min(currentProgress, 98), 
                            currentPhase.step
                        );
                    }
                }
            }, 800); // 每0.8秒更新一次，更频繁的反馈
            
            const response = await fetch(`${this.apiBaseUrl}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            });

            // 停止进度动画
            if (progressInterval) {
                clearInterval(progressInterval);
                progressInterval = null;
            }
            
            this.showLoadingProgress('⚡ Step 2/4: Processing content', 'Extracting and analyzing page elements...', 75, 3);
            
            await new Promise(resolve => setTimeout(resolve, 300)); // Brief pause for UX

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            this.showLoadingProgress('🎯 Step 3/4: Calculating SEO score', 'Running final optimization analysis...', 90, 4);
            
            const result = await response.json();
            
            if (result.error) {
                throw new Error(result.error);
            }
            
            this.showLoadingProgress('✨ Step 4/4: Generating insights', 'Preparing your personalized SEO report...', 100, 4);
            
            await new Promise(resolve => setTimeout(resolve, 500)); // Final pause for completion effect
            
            // Usage tracking removed - unlimited free service
            
            this.currentAnalysis = result;
            
            // Handle the new optimized response format
            const analysisData = result.analysis || result;
            
            this.showResults();
            this.updateAllSections(analysisData);
            this.generateTodos(analysisData);
            
            // 🎯 CHART INTEGRATION: Update charts after analysis completes
            if (window.seoChartManager) {
                console.log('🎯 Triggering chart updates with analysis data');
                setTimeout(() => {
                    window.seoChartManager.updateChartsWithAnalysis(result);
                }, 300); // Small delay to ensure DOM is ready
            } else {
                console.warn('⚠️ Chart manager not available');
            }
            
            // Show performance info if available
            if (result.performance) {
                console.log(`✅ Analysis completed in ${result.performance.execution_time}s (optimized: ${result.performance.optimized})`);
            }
            
            this.showAlert('🎉 SEO Analysis Complete! Your website has been thoroughly scanned.', 'success');
            
        } catch (error) {
            console.error('Analysis failed:', error);
            
            // Ensure progress interval is cleared in case of error
            if (progressInterval) {
                clearInterval(progressInterval);
                progressInterval = null;
            }
            
            // Show more specific error message based on error type
            let errorMessage = 'Analysis failed, please check network connection or URL';
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                errorMessage = 'Cannot connect to SEO analyzer API. Please ensure the server is running.';
            } else if (error.message) {
                errorMessage = `Analysis failed: ${error.message}`;
            }
            
            this.showAlert(errorMessage, 'error');
        } finally {
            // Final cleanup
            if (progressInterval) {
                clearInterval(progressInterval);
            }
            this.showLoading(false);
        }
    }

    showResults() {
        const resultsContainer = document.getElementById('resultsContainer');
        if (resultsContainer) {
            // Professional reveal animation
            resultsContainer.style.opacity = '0';
            resultsContainer.style.transform = 'translateY(20px)';
            resultsContainer.classList.remove('hidden');
            
            // Smooth fade-in with stagger effect
            setTimeout(() => {
                resultsContainer.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                resultsContainer.style.opacity = '1';
                resultsContainer.style.transform = 'translateY(0)';
                
                // Add stagger animation to each section
                const sections = resultsContainer.querySelectorAll('.bg-white');
                sections.forEach((section, index) => {
                    section.style.opacity = '0';
                    section.style.transform = 'translateY(30px)';
                    section.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                    
                    setTimeout(() => {
                        section.style.opacity = '1';
                        section.style.transform = 'translateY(0)';
                    }, index * 150 + 300);
                });
            }, 100);
            
            // Smooth scroll to results with professional timing
            setTimeout(() => {
                resultsContainer.scrollIntoView({ 
                    behavior: 'smooth',
                    block: 'start'
                });
            }, 800);
            
        }
        
        // Enable download report button after analysis is complete
        const downloadReportBtn = document.getElementById('downloadReportBtn');
        if (downloadReportBtn) {
            downloadReportBtn.disabled = false;
        }
    }

    updateAllSections(data) {
        console.log('🎯 DEBUG: UpdateAllSections called with data structure:', {
            hasAnalysis: !!data.analysis,
            hasPages: !!(data.analysis && data.analysis.pages),
            pageCount: data.analysis?.pages?.length || 0,
            firstPageKeys: data.analysis?.pages?.[0] ? Object.keys(data.analysis.pages[0]) : [],
            sampleInternalLinks: data.analysis?.pages?.[0]?.internal_links?.slice(0, 2) || 'none',
            sampleExternalLinks: data.analysis?.pages?.[0]?.external_links?.slice(0, 2) || 'none'
        });
        
        this.updateSiteInfo(data);
        this.updateSummarySection(data);
        this.updateSEOAnalysisSection(data);
        this.updateProfessionalDiagnostics(data);
        this.updateComplianceSection(data);
        this.updateLinksSection(data);
        this.updateSEOStrategySection();
        this.initSectionContent(this.currentSection);
    }

    updateSiteInfo(data) {
        const siteUrlElement = document.getElementById('siteUrl');
        if (siteUrlElement && this.currentAnalysis) {
            const url = data.pages?.[0]?.url || document.getElementById('urlInput')?.value || '';
            siteUrlElement.textContent = url;
        }
    }

    updateSummarySection(data) {
        this.updateSEOScoreDisplay(data);
        this.updateIssuesOverview(data);
    }

    updateSEOScoreDisplay(data) {
        // Add try-catch to prevent any color-related errors
        try {
            const scoreElement = document.getElementById('seoScore');
            const scoreCircle = document.getElementById('scoreCircle');
            const scoreNumber = document.getElementById('scoreNumber');
            const totalIssuesCount = document.getElementById('totalIssuesCount');
            const criticalCount = document.getElementById('criticalCount');
            const warningsCount = document.getElementById('warningsCount');
            const passedCount = document.getElementById('passedCount');
            const scoreDescription = document.getElementById('scoreDescription');
            
            // 🎯 UNIFIED SCORING SYSTEM - Enhanced consistency with backend
            let score = 0; // Start with 0 instead of arbitrary 75
            let scoreSource = 'none_found';
            
            console.log('=== 🎯 UNIFIED SEO SCORE DEBUG ===');
            console.log('Current Analysis Object:', this.currentAnalysis);
            console.log('Data Parameter:', data);
            
            // 🥇 PRIORITY 1: Backend Unified SEO Score (Most Accurate)
            if (this.currentAnalysis?.seo_score !== undefined) {
                const scoreData = this.currentAnalysis.seo_score;
                if (typeof scoreData === 'object' && scoreData.score !== undefined && scoreData.score !== null) {
                    score = Math.round(scoreData.score * 10) / 10;
                    scoreSource = scoreData.source || 'backend_unified';
                    console.log('✅ Using Backend Unified Score:', score, 'Source:', scoreData.source);
                } else if (typeof scoreData === 'number' && !isNaN(scoreData) && scoreData > 0) {
                    score = Math.round(scoreData * 10) / 10;
                    scoreSource = 'backend_number';
                    console.log('✅ Using Backend Number Score:', score);
                }
            }
            
            // 🥈 PRIORITY 2: Professional Analysis Overall Score (Fallback)
            if (score === 0 && this.currentAnalysis?.analysis?.pages?.[0]?.professional_analysis?.overall_score !== undefined) {
                const professionalScore = this.currentAnalysis.analysis.pages[0].professional_analysis.overall_score;
                if (professionalScore !== null && !isNaN(professionalScore) && professionalScore > 0) {
                    score = Math.round(professionalScore * 10) / 10;
                    scoreSource = 'professional_analysis';
                    console.log('✅ Using Professional Analysis Score:', score);
                }
            }
            
            // 🥉 PRIORITY 3: Frontend Calculation (Last Resort)
            if (score === 0) {
                score = this.calculateSEOScore(data);
                scoreSource = 'frontend_calculation';
                console.log('⚠️ Using Frontend Calculation Score (Last Resort):', score);
            }
            
            // Ensure score is within valid range
            score = Math.max(0, Math.min(100, score));
            
            console.log('🎯 Final Unified Score:', score, 'Source:', scoreSource);
            console.log('=== End Unified Score Debug ===');
            
            // Professional color scheme based on score
            let color = '#ef4444';
            let glowColor = 'rgba(239, 68, 68, 0.3)';
            let grade = 'F';
        
        if (score >= 90) {
            color = '#10b981';
            glowColor = 'rgba(16, 185, 129, 0.4)';
            grade = 'A+';
        } else if (score >= 80) {
            color = '#059669';
            glowColor = 'rgba(5, 150, 105, 0.4)';
            grade = 'A';
        } else if (score >= 70) {
            color = '#84cc16';
            glowColor = 'rgba(132, 204, 22, 0.4)';
            grade = 'B+';
        } else if (score >= 60) {
            color = '#eab308';
            glowColor = 'rgba(234, 179, 8, 0.4)';
            grade = 'B';
        } else if (score >= 50) {
            color = '#f59e0b';
            glowColor = 'rgba(245, 158, 11, 0.4)';
            grade = 'C';
        } else if (score >= 40) {
            color = '#f97316';
            glowColor = 'rgba(249, 115, 22, 0.4)';
            grade = 'D';
        }
        
        // Professional score animation with easing
        if (scoreElement && scoreNumber) {
            scoreElement.textContent = score.toFixed(1);
            scoreNumber.textContent = Math.round(score);
            scoreElement.style.color = color;
            scoreNumber.style.color = color;
        }
        
        // Enhanced circular progress with gradient and glow effects
        if (scoreCircle) {
            const circumference = 100;
            const progress = (score / 100) * circumference;
            
            // Animate the circle progress
            scoreCircle.style.transition = 'stroke-dasharray 2s cubic-bezier(0.4, 0, 0.2, 1)';
            scoreCircle.style.strokeDasharray = `${progress}, ${circumference}`;
            
            scoreCircle.style.stroke = color;
            scoreCircle.style.filter = `drop-shadow(0 0 8px ${glowColor})`;
            
            // Add grade indicator
            const gradeElement = document.querySelector('.score-grade');
            if (gradeElement) {
                gradeElement.textContent = grade;
                gradeElement.style.color = color;
            }
        }
        
        // Update issues count display - prioritize professional analysis
        const professionalAnalysis = this.currentAnalysis?.analysis?.pages?.[0]?.professional_analysis;
        let issues = { critical: 0, warnings: 0, passed: 0 };
        
        if (professionalAnalysis && professionalAnalysis.issues_summary) {
            const issuesSummary = professionalAnalysis.issues_summary;
            issues = {
                critical: issuesSummary.critical || 0,
                warnings: (issuesSummary.high || 0) + (issuesSummary.medium || 0),
                passed: Math.max(0, 150 - (issuesSummary.total_issues || 0)) // Professional analysis ~150 checks
            };
        } else {
            // Fallback to basic analysis
            issues = this.analyzeIssues(data);
        }
        
        if (criticalCount) {
            criticalCount.textContent = issues.critical;
            criticalCount.parentElement.style.transform = issues.critical > 0 ? 'scale(1.05)' : 'scale(1)';
        }
        
        if (warningsCount) {
            warningsCount.textContent = issues.warnings;
            warningsCount.parentElement.style.transform = issues.warnings > 0 ? 'scale(1.02)' : 'scale(1)';
        }
        
        if (passedCount) {
            passedCount.textContent = issues.passed;
            passedCount.parentElement.style.opacity = issues.passed > 10 ? '1' : '0.8';
        }
        
        if (totalIssuesCount) {
            const totalIssues = issues.critical + issues.warnings;
            totalIssuesCount.textContent = totalIssues;
            
            // Professional description with dynamic messaging and source indicator
            if (scoreDescription) {
                let statusMessage = '';
                if (score >= 90) {
                    statusMessage = 'Excellent! Your website has outstanding SEO optimization with minimal issues to address.';
                } else if (score >= 80) {
                    statusMessage = 'Great! Your website has strong SEO fundamentals with only minor improvements needed.';
                } else if (score >= 70) {
                    statusMessage = 'Good! Your website has solid SEO basics, but there are opportunities for significant improvement.';
                } else if (score >= 60) {
                    statusMessage = 'Fair. Your website needs attention to improve search engine visibility and ranking potential.';
                } else {
                    statusMessage = 'Critical issues detected! Immediate action is required to improve your website\'s SEO performance.';
                }
                
                scoreDescription.innerHTML = `
                    <p class="text-gray-700 mb-2">${statusMessage}</p>
                    <p class="text-sm text-gray-600">
                        SEO Score: <strong class="text-gray-900" style="color: ${color}">${score.toFixed(1)}/100</strong> | 
                        Issues to fix: <strong class="text-red-600">${totalIssues}</strong> | 
                        Checks passed: <strong class="text-green-600">${issues.passed}</strong>
                    </p>
                    <p class="text-xs text-gray-500 mt-1">Score source: ${scoreSource}</p>
                `;
            }
        }
        
        // Add professional animations to the score container
        const scoreContainer = scoreElement?.closest('.score-circle-large');
        if (scoreContainer) {
            scoreContainer.style.transform = 'scale(1)';
            scoreContainer.style.transition = 'transform 0.3s ease';
            setTimeout(() => {
                scoreContainer.style.transform = 'scale(1.02)';
                setTimeout(() => {
                    scoreContainer.style.transform = 'scale(1)';
                }, 200);
            }, 1000);
        }
        } catch (error) {
            console.error('Error in updateSEOScoreDisplay:', error);
            console.error('Error details:', {
                currentAnalysis: this.currentAnalysis,
                data: data,
                errorStack: error.stack
            });
            // Fallback in case of any error
            const scoreElement = document.getElementById('seoScore');
            if (scoreElement) {
                scoreElement.textContent = '75.0';
                scoreElement.style.color = '#f59e0b';
            }
        }
    }

    calculateSEOScore(data) {
        // Use the same weighted scoring algorithm as the report generator for consistency
        if (!data.pages || data.pages.length === 0) return 75; // Default fallback
        
        const page = data.pages[0];
        const scores = [];
        const weights = {};
        
        // Title score (weight: 20%)
        if (page.title !== undefined) {
            const titleLength = page.title ? page.title.length : 0;
            if (titleLength >= 50 && titleLength <= 60) {
                scores.push(100);
            } else if (titleLength >= 30 && titleLength <= 70) {
                scores.push(80);
            } else {
                scores.push(40);
            }
            weights.title = 0.20;
        }
        
        // Description score (weight: 15%)
        if (page.description !== undefined) {
            const descLength = page.description ? page.description.length : 0;
            if (descLength >= 140 && descLength <= 160) {
                scores.push(100);
            } else if (descLength >= 120 && descLength <= 180) {
                scores.push(80);
            } else {
                scores.push(40);
            }
            weights.description = 0.15;
        }
        
        // Headings score (weight: 15%)
        const h1Count = page.headings?.h1?.length || 0;
        if (h1Count === 1) {
            scores.push(100);
        } else if (h1Count === 0) {
            scores.push(20);
        } else {
            scores.push(60);
        }
        weights.headings = 0.15;
        
        // Images score - use warnings to determine missing alt tags (weight: 10%)
        const warnings = page.warnings || [];
        const imageWarnings = warnings.filter(w => typeof w === 'string' && w.includes('Image missing alt tag'));
        if (imageWarnings.length === 0) {
            scores.push(100);
        } else if (imageWarnings.length <= 2) {
            scores.push(70);
        } else {
            scores.push(30);
        }
        weights.images = 0.10;
        
        // Content score (weight: 25%)
        const wordCount = page.word_count || 0;
        if (wordCount >= 300) {
            scores.push(100);
        } else if (wordCount >= 150) {
            scores.push(80);
        } else if (wordCount >= 50) {
            scores.push(60);
        } else {
            scores.push(30);
        }
        weights.content = 0.25;
        
        // Links/warnings score (weight: 15%)
        if (warnings.length === 0) {
            scores.push(100);
        } else if (warnings.length <= 3) {
            scores.push(70);
        } else {
            scores.push(40);
        }
        weights.links = 0.15;
        
        // Calculate weighted average
        if (scores.length > 0) {
            const totalWeight = Object.values(weights).reduce((sum, weight) => sum + weight, 0);
            if (totalWeight > 0) {
                const weightedScore = scores.reduce((sum, score, index) => {
                    const weightKey = Object.keys(weights)[index];
                    return sum + (score * weights[weightKey]);
                }, 0) / totalWeight;
                return Math.round(weightedScore * 10) / 10; // Round to 1 decimal place
            }
        }
        
        return 75.0; // Fallback score
    }

    analyzeIssues(data) {
        const issues = { critical: 0, warnings: 0, passed: 0 };
        
        if (data.pages && data.pages.length > 0) {
            const page = data.pages[0];
            
            if (!page.description || page.description.length < 120) issues.critical++;
            if (page.images && page.images.some(img => !img.alt)) issues.critical++;
            if (!page.h1 || page.h1.length === 0) issues.critical++;
            
            if (page.title && (page.title.length < 30 || page.title.length > 60)) issues.warnings++;
            if (page.canonical && page.canonical !== page.url) issues.warnings++;
            
            issues.passed = 15 - issues.critical - issues.warnings;
        } else {
            issues.critical = 4;
            issues.warnings = 2;
            issues.passed = 12;
        }
        
        return issues;
    }

    updateIssuesOverview(data) {
        const container = document.getElementById('issuesContainer');
        if (!container) return;
        
        const issues = this.generateIssuesList(data);
        
        container.innerHTML = issues.map(issue => `
            <div class="issue-card ${issue.type} p-4">
                <div class="flex items-center justify-between">
                    <div class="flex items-center">
                        <i class="${issue.icon} ${issue.type === 'critical' ? 'text-red-500' : 'text-yellow-500'} mr-3"></i>
                        <div>
                            <h4 class="font-semibold text-gray-900">${issue.title}</h4>
                            <p class="text-sm text-gray-600">${issue.message}</p>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    generateIssuesList(data) {
        const issues = [];
        
        if (data.pages && data.pages.length > 0) {
            const page = data.pages[0];
            
            if (!page.description || page.description.length < 120) {
                issues.push({
                    type: 'critical',
                    icon: 'fas fa-times-circle',
                    title: 'Description',
                    message: 'Meta description is too short or missing — expand to at least 140 characters.'
                });
            }
            
            if (page.images && page.images.some(img => !img.alt)) {
                const missingAlt = page.images.filter(img => !img.alt).length;
                issues.push({
                    type: 'critical',
                    icon: 'fas fa-times-circle',
                    title: 'Image Alt',
                    message: `Some images on your page have no alt attribute. (${missingAlt})`
                });
            }
            
            if (page.title && (page.title.length < 30 || page.title.length > 60)) {
                issues.push({
                    type: 'warning',
                    icon: 'fas fa-exclamation-triangle',
                    title: 'Title',
                    message: `Meta title length is ${page.title.length < 30 ? 'too short' : 'too long'} — aim for 50-60 characters.`
                });
            }
        } else {
            issues.push(
                {
                    type: 'critical',
                    icon: 'fas fa-times-circle',
                    title: 'Description',
                    message: 'Meta description is too short (30 characters) — expand to at least 140 characters.'
                },
                {
                    type: 'critical',
                    icon: 'fas fa-times-circle',
                    title: 'Image Alt',
                    message: 'Some images on your page have no alt attribute. (2)'
                },
                {
                    type: 'warning',
                    icon: 'fas fa-exclamation-triangle',
                    title: 'Title',
                    message: 'Meta title is a bit short (33 characters) — aim for 50-60 characters.'
                }
            );
        }
        
        return issues;
    }

    updateSEOAnalysisSection(data) {
        if (!data.pages || data.pages.length === 0) return;
        
        const page = data.pages[0];
        
        const analyzedUrl = document.getElementById('analyzedUrl');
        if (analyzedUrl) analyzedUrl.textContent = page.url || '';
        
        const canonicalUrl = document.getElementById('canonicalUrl');
        if (canonicalUrl) canonicalUrl.textContent = page.canonical || page.url || '';
        
        const pageTitle = document.getElementById('pageTitle');
        if (pageTitle) pageTitle.textContent = page.title || 'No title found';
        
        const pageDescription = document.getElementById('pageDescription');
        if (pageDescription) pageDescription.textContent = page.description || 'No meta description found';
        
        const h1Text = document.getElementById('h1Text');
        if (h1Text) {
            const h1 = page.h1 && page.h1.length > 0 ? page.h1[0] : 'No H1 found';
            h1Text.textContent = h1;
        }
        
        this.updateHeadingStructure(page);
        this.updateKeywordDensity(data);
        this.updateImagesList(page);
        this.updateTrendsAnalysis(data); // 🔥 Add trends analysis update
    }

    updateHeadingStructure(page) {
        const container = document.getElementById('headingStructure');
        if (!container) return;
        
        const headingData = this.extractHeadingData(page) || [
            { level: 'H1', frequency: 1, value: page.h1?.[0] || 'Main Heading' },
            { level: 'H2', frequency: page.h2?.length || 3, value: page.h2?.[0] || 'Section Heading' },
            { level: 'H3', frequency: page.h3?.length || 5, value: page.h3?.[0] || 'Subsection Heading' },
            { level: 'H4', frequency: page.h4?.length || 2, value: page.h4?.[0] || 'Sub-subsection Heading' }
        ];
        
        container.innerHTML = headingData.map(heading => `
            <div class="flex items-center space-x-4 py-2">
                <span class="text-sm font-medium w-16">${heading.level}</span>
                <div class="w-24">
                    <div class="flex items-center space-x-2">
                        <span class="text-sm">${heading.frequency}</span>
                        <div class="flex-1 bg-gray-200 rounded-full h-2">
                            <div class="frequency-bar rounded-full h-2" style="width: ${Math.min(heading.frequency * 10, 100)}%"></div>
                        </div>
                    </div>
                </div>
                <span class="text-sm text-gray-600 flex-1">${heading.value || ''}</span>
            </div>
        `).join('');
    }

    extractHeadingData(page) {
        const headings = [];
        ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'].forEach(tag => {
            if (page[tag] && page[tag].length > 0) {
                headings.push({
                    level: tag.toUpperCase(),
                    frequency: page[tag].length,
                    value: page[tag][0]
                });
            }
        });
        return headings.length > 0 ? headings : null;
    }

    updateKeywordDensity(data) {
        const table = document.getElementById('keywordDensityTable');
        if (!table) return;
        
        const keywords = data.keywords || [
            { keyword: 'seo', count: 20, density: 2.5 },
            { keyword: 'analysis', count: 15, density: 1.9 },
            { keyword: 'website', count: 12, density: 1.5 },
            { keyword: 'optimization', count: 10, density: 1.2 },
            { keyword: 'content', count: 8, density: 1.0 }
        ];
        
        table.innerHTML = keywords.slice(0, 10).map(item => `
            <tr class="hover:bg-gray-50">
                <td class="py-2 text-sm">${item.keyword || item.word}</td>
                <td class="py-2 text-sm">${item.count || item.repeats}</td>
                <td class="py-2 text-sm">${(item.density || (item.count / 400 * 100)).toFixed(1)}%</td>
            </tr>
        `).join('');
    }

    updateImagesList(page) {
        const container = document.getElementById('imagesList');
        if (!container) return;
        
        if (page.images && page.images.length > 0) {
            const imagesWithoutAlt = page.images.filter(img => !img.alt);
            container.innerHTML = imagesWithoutAlt.map(img => `
                <div class="text-sm text-blue-600">${img.src}</div>
            `).join('') || '<div class="text-sm text-green-600">All images have alt attributes</div>';
        } else {
            container.innerHTML = '<div class="text-sm text-gray-500">No images found</div>';
        }
    }

    updateTrendsAnalysisSection() {
        // Fetch trends data from backend API and update the trends section
        this.fetchTrendsData();
    }

    async fetchTrendsData() {
        const urlInput = document.getElementById('urlInput');
        const url = urlInput?.value?.trim();
        
        if (!url || !this.currentAnalysis) {
            this.updateTrendsPlaceholder('No URL available for trends analysis');
            return;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/trends/analysis`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            });

            if (!response.ok) {
                throw new Error(`Trends API error: ${response.status}`);
            }

            const trendsData = await response.json();
            console.log('🔥 Trends data received:', trendsData);
            
            this.updateTrendsDisplay(trendsData);
            
        } catch (error) {
            console.error('Failed to fetch trends data:', error);
            this.updateTrendsPlaceholder(`Trends analysis unavailable: ${error.message}`);
        }
    }

    updateTrendsDisplay(trendsData) {
        // Update all trends components with fetched data
        this.updateKeywordTrendsTable(trendsData.keyword_trends || []);
        this.updateContentOpportunities(trendsData.content_opportunities || []);
        this.updateTrendingTopics(trendsData.trending_topics || []);
        this.updateSeasonalInsights(trendsData.seasonal_insights || {});
        this.updateCompetitiveAnalysis(trendsData.competitive_analysis || {});
        this.createTrendsCharts(trendsData);
    }

    updateKeywordTrendsTable(keywordTrends) {
        const container = document.getElementById('keywordTrendsTable');
        if (!container) {
            console.warn('Keyword trends table container not found');
            return;
        }

        if (!keywordTrends || keywordTrends.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center py-4">No keyword trends data available</p>';
            return;
        }

        const tableHTML = `
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Keyword</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Interest Score</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Trend</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Related Queries</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        ${keywordTrends.slice(0, 10).map(trend => {
                            const trendIcon = trend.trend_direction === 'rising' ? '📈' : 
                                            trend.trend_direction === 'falling' ? '📉' : '➡️';
                            const trendColor = trend.trend_direction === 'rising' ? 'text-green-600' : 
                                             trend.trend_direction === 'falling' ? 'text-red-600' : 'text-gray-600';
                            
                            return `
                                <tr class="hover:bg-gray-50">
                                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                        ${trend.keyword || 'Unknown'}
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                        <div class="flex items-center">
                                            <div class="w-16 bg-gray-200 rounded-full h-2 mr-2">
                                                <div class="bg-blue-600 h-2 rounded-full" style="width: ${trend.interest_score || 0}%"></div>
                                            </div>
                                            <span>${trend.interest_score || 0}%</span>
                                        </div>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap text-sm ${trendColor}">
                                        <span class="inline-flex items-center">
                                            ${trendIcon} ${trend.trend_direction || 'stable'}
                                        </span>
                                    </td>
                                    <td class="px-6 py-4 text-sm text-gray-500">
                                        <div class="max-w-xs truncate">
                                            ${(trend.related_queries || []).slice(0, 3).join(', ') || 'No related queries'}
                                        </div>
                                    </td>
                                </tr>
                            `;
                        }).join('')}
                    </tbody>
                </table>
            </div>
        `;

        container.innerHTML = tableHTML;
    }

    updateContentOpportunities(opportunities) {
        const container = document.getElementById('contentOpportunities');
        if (!container) {
            console.warn('Content opportunities container not found');
            return;
        }

        if (!opportunities || opportunities.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center py-4">No content opportunities identified</p>';
            return;
        }

        const opportunitiesHTML = `
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                ${opportunities.slice(0, 9).map(opp => {
                    const priorityClass = {
                        'high': 'border-red-200 bg-red-50',
                        'medium': 'border-yellow-200 bg-yellow-50',
                        'low': 'border-green-200 bg-green-50'
                    }[opp.priority] || 'border-gray-200 bg-gray-50';
                    
                    const priorityIcon = {
                        'high': '🔥',
                        'medium': '⚡',
                        'low': '💡'
                    }[opp.priority] || '📝';

                    return `
                        <div class="border ${priorityClass} rounded-lg p-4 hover:shadow-md transition-shadow">
                            <div class="flex items-start justify-between mb-2">
                                <h4 class="text-sm font-semibold text-gray-900 flex-1">
                                    ${priorityIcon} ${opp.topic || 'Content Topic'}
                                </h4>
                                <span class="text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-800">
                                    ${opp.priority || 'medium'}
                                </span>
                            </div>
                            <p class="text-sm text-gray-600 mb-3">
                                ${opp.description || 'Content opportunity description'}
                            </p>
                            <div class="flex justify-between items-center text-xs text-gray-500">
                                <span>Search Volume: ${opp.search_volume || 'N/A'}</span>
                                <span>Competition: ${opp.competition || 'Unknown'}</span>
                            </div>
                            ${opp.related_keywords && opp.related_keywords.length > 0 ? `
                                <div class="mt-2 pt-2 border-t border-gray-200">
                                    <p class="text-xs text-gray-500 mb-1">Related Keywords:</p>
                                    <div class="flex flex-wrap gap-1">
                                        ${opp.related_keywords.slice(0, 3).map(kw => 
                                            `<span class="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded">${kw}</span>`
                                        ).join('')}
                                    </div>
                                </div>
                            ` : ''}
                        </div>
                    `;
                }).join('')}
            </div>
        `;

        container.innerHTML = opportunitiesHTML;
    }

    updateTrendingTopics(trendingTopics) {
        const container = document.getElementById('trendingTopics');
        if (!container) {
            console.warn('Trending topics container not found');
            return;
        }

        if (!trendingTopics || trendingTopics.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center py-4">No trending topics available</p>';
            return;
        }

        const topicsHTML = `
            <div class="space-y-3">
                ${trendingTopics.slice(0, 8).map((topic, index) => {
                    const rankIcon = index < 3 ? ['🥇', '🥈', '🥉'][index] : `${index + 1}`;
                    const trendPercent = topic.growth_rate || 0;
                    const trendColor = trendPercent > 0 ? 'text-green-600' : 
                                     trendPercent < 0 ? 'text-red-600' : 'text-gray-600';
                    
                    return `
                        <div class="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50">
                            <div class="flex items-center space-x-3 flex-1">
                                <span class="text-lg font-bold text-gray-400 w-8">${rankIcon}</span>
                                <div class="flex-1">
                                    <h4 class="text-sm font-medium text-gray-900">${topic.topic || topic.title || 'Trending Topic'}</h4>
                                    <p class="text-xs text-gray-500">${topic.category || 'General'}</p>
                                </div>
                            </div>
                            <div class="text-right">
                                <div class="text-sm font-medium ${trendColor}">
                                    ${trendPercent > 0 ? '+' : ''}${trendPercent}%
                                </div>
                                <div class="text-xs text-gray-500">
                                    ${topic.search_volume || 'N/A'} searches
                                </div>
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;

        container.innerHTML = topicsHTML;
    }

    updateSeasonalInsights(seasonalData) {
        const container = document.getElementById('seasonalInsights');
        if (!container) {
            console.warn('Seasonal insights container not found');
            return;
        }

        if (!seasonalData || Object.keys(seasonalData).length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center py-4">No seasonal insights available</p>';
            return;
        }

        const insights = seasonalData.insights || [];
        const currentSeason = seasonalData.current_season || 'Unknown';
        const seasonalScore = seasonalData.seasonal_score || 0;

        const insightsHTML = `
            <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 mb-4">
                <div class="flex items-center justify-between mb-3">
                    <h4 class="text-lg font-semibold text-gray-900">🌟 Current Season: ${currentSeason}</h4>
                    <div class="text-right">
                        <div class="text-sm text-gray-600">Seasonal Relevance Score</div>
                        <div class="text-xl font-bold text-indigo-600">${seasonalScore}/100</div>
                    </div>
                </div>
                ${insights.length > 0 ? `
                    <div class="space-y-2">
                        ${insights.slice(0, 5).map(insight => `
                            <div class="flex items-start space-x-2 text-sm">
                                <span class="text-indigo-500">•</span>
                                <span class="text-gray-700">${insight.message || insight}</span>
                            </div>
                        `).join('')}
                    </div>
                ` : '<p class="text-gray-600 text-sm">No specific seasonal insights available</p>'}
            </div>
        `;

        container.innerHTML = insightsHTML;
    }

    updateCompetitiveAnalysis(competitiveData) {
        const container = document.getElementById('competitiveAnalysis');
        if (!container) {
            console.warn('Competitive analysis container not found');
            return;
        }

        if (!competitiveData || Object.keys(competitiveData).length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center py-4">No competitive analysis available</p>';
            return;
        }

        const competitors = competitiveData.competitors || [];
        const marketShare = competitiveData.market_share || 0;
        const competitiveGaps = competitiveData.gaps || [];

        const competitiveHTML = `
            <div class="space-y-4">
                <!-- Market Position -->
                <div class="bg-gray-50 rounded-lg p-4">
                    <h4 class="text-md font-semibold text-gray-900 mb-2">📊 Market Position</h4>
                    <div class="flex items-center space-x-4">
                        <div class="flex-1">
                            <div class="text-sm text-gray-600">Estimated Market Share</div>
                            <div class="text-2xl font-bold text-blue-600">${marketShare.toFixed(1)}%</div>
                        </div>
                        <div class="w-24 bg-gray-200 rounded-full h-3">
                            <div class="bg-blue-600 h-3 rounded-full" style="width: ${marketShare}%"></div>
                        </div>
                    </div>
                </div>

                <!-- Top Competitors -->
                ${competitors.length > 0 ? `
                    <div class="bg-white border border-gray-200 rounded-lg p-4">
                        <h4 class="text-md font-semibold text-gray-900 mb-3">🏆 Top Competitors</h4>
                        <div class="space-y-2">
                            ${competitors.slice(0, 5).map((comp, index) => `
                                <div class="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0">
                                    <div class="flex items-center space-x-3">
                                        <span class="w-6 h-6 rounded-full bg-gray-100 flex items-center justify-center text-xs font-medium">
                                            ${index + 1}
                                        </span>
                                        <span class="text-sm font-medium text-gray-900">${comp.domain || comp.name || 'Unknown'}</span>
                                    </div>
                                    <div class="text-sm text-gray-600">
                                        ${comp.market_share ? `${comp.market_share}% share` : 'Competitor'}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}

                <!-- Competitive Gaps -->
                ${competitiveGaps.length > 0 ? `
                    <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                        <h4 class="text-md font-semibold text-gray-900 mb-3">⚠️ Competitive Gaps</h4>
                        <div class="space-y-2">
                            ${competitiveGaps.slice(0, 4).map(gap => `
                                <div class="flex items-start space-x-2 text-sm">
                                    <span class="text-yellow-600 mt-0.5">⚡</span>
                                    <span class="text-gray-700">${gap.description || gap}</span>
                                    ${gap.priority ? `<span class="ml-auto text-xs px-2 py-1 rounded bg-yellow-200 text-yellow-800">${gap.priority}</span>` : ''}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;

        container.innerHTML = competitiveHTML;
    }

    createTrendsCharts(trendsData) {
        // Create interactive charts for trends visualization
        this.createKeywordTrendsChart(trendsData.keyword_trends || []);
        this.createOpportunityChart(trendsData.content_opportunities || []);
        this.createSeasonalChart(trendsData.seasonal_insights || {});
    }

    createKeywordTrendsChart(keywordTrends) {
        const canvas = document.getElementById('keywordTrendsChart');
        if (!canvas || !keywordTrends.length) return;

        // Destroy existing chart
        if (this.charts?.keywordTrends) {
            this.charts.keywordTrends.destroy();
        }

        if (!this.charts) this.charts = {};

        const ctx = canvas.getContext('2d');
        this.charts.keywordTrends = new Chart(ctx, {
            type: 'line',
            data: {
                labels: keywordTrends.slice(0, 8).map(trend => trend.keyword),
                datasets: [{
                    label: 'Search Interest Trend',
                    data: keywordTrends.slice(0, 8).map(trend => trend.interest_score || 0),
                    borderColor: 'rgba(59, 130, 246, 1)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Keyword Interest Trends',
                        font: { size: 14, weight: 'bold' }
                    },
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Interest Score (%)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Keywords'
                        },
                        ticks: {
                            maxRotation: 45
                        }
                    }
                }
            }
        });

        console.log('✅ Keyword trends chart created successfully');
    }

    createOpportunityChart(opportunities) {
        const canvas = document.getElementById('opportunityChart');
        if (!canvas || !opportunities.length) return;

        // Destroy existing chart
        if (this.charts?.opportunity) {
            this.charts.opportunity.destroy();
        }

        if (!this.charts) this.charts = {};

        const priorityCounts = {
            high: opportunities.filter(opp => opp.priority === 'high').length,
            medium: opportunities.filter(opp => opp.priority === 'medium').length,
            low: opportunities.filter(opp => opp.priority === 'low').length
        };

        const ctx = canvas.getContext('2d');
        this.charts.opportunity = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['High Priority', 'Medium Priority', 'Low Priority'],
                datasets: [{
                    data: [priorityCounts.high, priorityCounts.medium, priorityCounts.low],
                    backgroundColor: [
                        'rgba(239, 68, 68, 0.8)',   // High - Red
                        'rgba(245, 158, 11, 0.8)',  // Medium - Orange
                        'rgba(16, 185, 129, 0.8)'   // Low - Green
                    ],
                    borderColor: [
                        'rgba(239, 68, 68, 1)',
                        'rgba(245, 158, 11, 1)',
                        'rgba(16, 185, 129, 1)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: `Content Opportunities (${opportunities.length} total)`,
                        font: { size: 14, weight: 'bold' }
                    },
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });

        console.log('✅ Opportunity chart created successfully');
    }

    updateTrendsPlaceholder(message) {
        // Show placeholder message for trends section
        const containers = [
            'keywordTrendsTable',
            'contentOpportunities', 
            'trendingTopics',
            'seasonalInsights',
            'competitiveAnalysis'
        ];

        containers.forEach(containerId => {
            const container = document.getElementById(containerId);
            if (container) {
                container.innerHTML = `<p class="text-gray-500 text-center py-8">${message}</p>`;
            }
        });
    }

    updateTrendsAnalysis(data) {
        // Updated trends analysis method that handles both data sources
        if (data && data.trends_insights) {
            // Use trends data if available
            this.updateTrendsDisplay(data.trends_insights);
        } else {
            // Fetch trends data from API
            this.fetchTrendsData();
        }
    }

    updateProfessionalDiagnostics(data) {
        // Check if professional analysis data exists
        if (!data.pages || !data.pages[0] || !data.pages[0].professional_analysis) {
            // Hide professional diagnostics section if no data
            const professionalSection = document.getElementById('professional-diagnostics');
            if (professionalSection) {
                const score = document.getElementById('professionalScore');
                if (score) score.innerHTML = '<i class="fas fa-info-circle mr-2"></i>Not Available';
                
                const categoryScores = document.getElementById('categoryScores');
                if (categoryScores) categoryScores.innerHTML = '<p class="text-gray-500 col-span-full text-center py-8">Professional diagnostics data not available for this analysis.</p>';
            }
            return;
        }

        const professionalData = data.pages[0].professional_analysis;
        
        // Update overall score
        const scoreElement = document.getElementById('professionalScore');
        if (scoreElement && professionalData.overall_score !== undefined) {
            const score = Math.round(professionalData.overall_score);
            const grade = professionalData.grade || this.getGradeFromScore(score);
            const colorClass = score >= 80 ? 'bg-green-100 text-green-800' : 
                              score >= 60 ? 'bg-yellow-100 text-yellow-800' : 
                              'bg-red-100 text-red-800';
            scoreElement.className = `inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${colorClass}`;
            scoreElement.innerHTML = `${score}/100 (${grade})`;
        }

        // Update category scores
        const categoryScoresElement = document.getElementById('categoryScores');
        if (categoryScoresElement && professionalData.category_scores) {
            categoryScoresElement.innerHTML = Object.entries(professionalData.category_scores).map(([key, category]) => {
                const score = Math.round(category.score);
                const colorClass = score >= 80 ? 'border-green-200 bg-green-50' : 
                                  score >= 60 ? 'border-yellow-200 bg-yellow-50' : 
                                  'border-red-200 bg-red-50';
                const iconColor = score >= 80 ? 'text-green-600' : 
                                 score >= 60 ? 'text-yellow-600' : 
                                 'text-red-600';
                
                return `
                    <div class="border ${colorClass} rounded-lg p-4">
                        <div class="flex items-center justify-between mb-2">
                            <h4 class="text-sm font-medium text-gray-900 capitalize">${category.category.replace(/_/g, ' ')}</h4>
                            <i class="fas fa-circle ${iconColor}"></i>
                        </div>
                        <div class="text-2xl font-bold text-gray-900 mb-1">${score}/100</div>
                        <div class="text-xs text-gray-500">
                            ${category.issues_found} issues found
                            ${category.critical_issues > 0 ? `<span class="text-red-600">(${category.critical_issues} critical)</span>` : ''}
                        </div>
                    </div>
                `;
            }).join('');
        }

        // Update issues summary
        const issuesSummaryElement = document.getElementById('issuesSummary');
        if (issuesSummaryElement && professionalData.issues_summary) {
            const summary = professionalData.issues_summary;
            issuesSummaryElement.innerHTML = `
                <div class="text-center">
                    <div class="text-2xl font-bold text-gray-900">${summary.total_issues || 0}</div>
                    <div class="text-sm text-gray-500">Total Issues</div>
                </div>
                <div class="text-center">
                    <div class="text-2xl font-bold text-red-600">${summary.critical || 0}</div>
                    <div class="text-sm text-gray-500">Critical</div>
                </div>
                <div class="text-center">
                    <div class="text-2xl font-bold text-yellow-600">${summary.high || 0}</div>
                    <div class="text-sm text-gray-500">High Priority</div>
                </div>
                <div class="text-center">
                    <div class="text-2xl font-bold text-blue-600">${summary.medium || 0}</div>
                    <div class="text-sm text-gray-500">Medium Priority</div>
                </div>
            `;
        }

        // Update professional issues list
        const professionalIssuesElement = document.getElementById('professionalIssues');
        if (professionalIssuesElement && professionalData.all_issues) {
            const issues = professionalData.all_issues.slice(0, 10); // Show top 10 issues
            if (issues.length > 0) {
                professionalIssuesElement.innerHTML = `
                    <div class="mb-4">
                        <h4 class="text-lg font-semibold text-gray-800 mb-4">Top Priority Issues</h4>
                        <div class="space-y-3">
                            ${issues.map(issue => {
                                const priorityColor = {
                                    'critical': 'border-red-500 bg-red-50',
                                    'high': 'border-orange-500 bg-orange-50', 
                                    'medium': 'border-yellow-500 bg-yellow-50',
                                    'low': 'border-blue-500 bg-blue-50'
                                }[issue.priority] || 'border-gray-500 bg-gray-50';
                                
                                const iconColor = {
                                    'critical': 'text-red-600',
                                    'high': 'text-orange-600',
                                    'medium': 'text-yellow-600', 
                                    'low': 'text-blue-600'
                                }[issue.priority] || 'text-gray-600';
                                
                                return `
                                    <div class="border-l-4 ${priorityColor} p-4 rounded-r-lg">
                                        <div class="flex items-start">
                                            <i class="fas fa-exclamation-triangle ${iconColor} mt-1 mr-3"></i>
                                            <div class="flex-1">
                                                <h5 class="font-medium text-gray-900">${issue.title}</h5>
                                                <p class="text-sm text-gray-600 mt-1">${issue.description}</p>
                                                <p class="text-sm text-blue-600 mt-2"><strong>Recommendation:</strong> ${issue.recommendation}</p>
                                                <div class="flex items-center mt-2 text-xs text-gray-500">
                                                    <span class="mr-4">Impact: ${Math.round(issue.impact_score)}/100</span>
                                                    <span class="mr-4">Effort: ${Math.round(issue.effort_score)}/100</span>
                                                    <span>ROI: ${Math.round(issue.roi_score * 10)/10}</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                `;
                            }).join('')}
                        </div>
                    </div>
                `;
            } else {
                professionalIssuesElement.innerHTML = '<p class="text-green-600 text-center py-8"><i class="fas fa-check-circle mr-2"></i>No critical issues found! Your website is in excellent shape.</p>';
            }
        }

        // Update optimization roadmap
        const optimizationRoadmapElement = document.getElementById('optimizationRoadmap');
        if (optimizationRoadmapElement && professionalData.optimization_roadmap) {
            const roadmap = professionalData.optimization_roadmap;
            optimizationRoadmapElement.innerHTML = `
                <div>
                    <h4 class="text-lg font-semibold text-gray-800 mb-4">📋 Optimization Roadmap</h4>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        ${Object.entries(roadmap).map(([phase, data], index) => {
                            const phaseNumber = index + 1;
                            const colorClass = index === 0 ? 'border-red-200 bg-red-50' :
                                              index === 1 ? 'border-yellow-200 bg-yellow-50' :
                                              'border-blue-200 bg-blue-50';
                            return `
                                <div class="border ${colorClass} rounded-lg p-4">
                                    <h5 class="font-medium text-gray-900 mb-2">Phase ${phaseNumber}</h5>
                                    <p class="text-sm text-gray-600 mb-2">${data.duration}</p>
                                    <p class="text-sm text-gray-600 mb-3">Expected Impact: ${data.expected_impact}</p>
                                    <div class="text-xs text-gray-500">${data.issues ? data.issues.length : 0} issues to address</div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            `;
        }
    }

    getGradeFromScore(score) {
        if (score >= 90) return 'A+';
        if (score >= 85) return 'A';
        if (score >= 80) return 'A-';
        if (score >= 75) return 'B+';
        if (score >= 70) return 'B';
        if (score >= 65) return 'B-';
        if (score >= 60) return 'C+';
        if (score >= 55) return 'C';
        if (score >= 50) return 'C-';
        if (score >= 40) return 'D';
        return 'F';
    }

    updateComplianceSection(data) {
        if (!data.pages || data.pages.length === 0) return;
        
        const page = data.pages[0];
        const baseUrl = new URL(page.url || 'https://example.com');
        
        const robotsUrl = document.getElementById('robotsUrl');
        if (robotsUrl) robotsUrl.textContent = `${baseUrl.origin}/robots.txt`;
        
        const sitemapUrl = document.getElementById('sitemapUrl');
        if (sitemapUrl) sitemapUrl.textContent = `${baseUrl.origin}/sitemap.xml`;
        
        const pageLang = document.getElementById('pageLang');
        if (pageLang) pageLang.textContent = page.lang || 'en';
        
        const faviconUrl = document.getElementById('faviconUrl');
        if (faviconUrl) faviconUrl.textContent = `${baseUrl.origin}/favicon.ico`;
    }

    updateLinksSection(data) {
        this.updateInternalLinks(data);
        this.updateExternalLinks(data);
    }

    updateInternalLinks(data) {
        const table = document.getElementById('internalLinksTable');
        const countElement = document.getElementById('internalLinksCount');
        
        if (!table) return;
        
        console.log('🔍 DEBUG: UpdateInternalLinks called with data:', data);
        console.log('🔍 DEBUG: Current analysis object:', this.currentAnalysis);
        
        const internalLinks = this.extractInternalLinks(data);
        
        if (!internalLinks || internalLinks.length === 0) {
            console.log('⚠️ DEBUG: No internal links found, using fallback data');
            // Only use fallback if extraction completely fails
            const fallbackLinks = [
                { url: 'https://example.com/', anchor: 'Home' },
                { url: 'https://example.com/about', anchor: 'About' },
                { url: 'https://example.com/services', anchor: 'Services' },
                { url: 'https://example.com/contact', anchor: 'Contact' }
            ];
            
            if (countElement) {
                countElement.textContent = `(Found ${fallbackLinks.length}) - Using Fallback Data`;
                countElement.style.color = '#ef4444'; // Red to indicate issue
            }
            
            table.innerHTML = fallbackLinks.map((link, index) => `
                <tr class="hover:bg-gray-50" style="background-color: #fef2f2;">
                    <td class="px-4 py-2 text-sm">${index + 1}</td>
                    <td class="px-4 py-2 text-sm text-red-600">${link.url}</td>
                    <td class="px-4 py-2 text-sm text-red-600">${link.anchor}</td>
                </tr>
            `).join('');
            return;
        }
        
        console.log(`✅ DEBUG: Successfully extracted ${internalLinks.length} internal links`);
        
        if (countElement) {
            countElement.textContent = `(Found ${internalLinks.length})`;
            countElement.style.color = '#10b981'; // Green to indicate success
        }
        
        table.innerHTML = internalLinks.map((link, index) => `
            <tr class="hover:bg-gray-50">
                <td class="px-4 py-2 text-sm">${index + 1}</td>
                <td class="px-4 py-2 text-sm text-blue-600">${link.url}</td>
                <td class="px-4 py-2 text-sm">${link.anchor}</td>
            </tr>
        `).join('');
    }

    updateExternalLinks(data) {
        const table = document.getElementById('externalLinksTable');
        const countElement = document.getElementById('externalLinksCount');
        
        if (!table) return;
        
        console.log('🔍 DEBUG: UpdateExternalLinks called with data:', data);
        
        const externalLinks = this.extractExternalLinks(data);
        
        if (!externalLinks || externalLinks.length === 0) {
            console.log('⚠️ DEBUG: No external links found, using fallback data');
            // Only use fallback if extraction completely fails
            const fallbackLinks = [
                { url: 'https://github.com/', anchor: 'GitHub' },
                { url: 'https://stackoverflow.com/', anchor: 'Stack Overflow' },
                { url: 'https://developer.mozilla.org/', anchor: 'MDN' }
            ];
            
            if (countElement) {
                countElement.textContent = `(Found ${fallbackLinks.length}) - Using Fallback Data`;
                countElement.style.color = '#ef4444'; // Red to indicate issue
            }
            
            table.innerHTML = fallbackLinks.map((link, index) => `
                <tr class="hover:bg-gray-50" style="background-color: #fef2f2;">
                    <td class="px-4 py-2 text-sm">${index + 1}</td>
                    <td class="px-4 py-2 text-sm text-red-600">${link.url}</td>
                    <td class="px-4 py-2 text-sm text-red-600">${link.anchor}</td>
                </tr>
            `).join('');
            return;
        }
        
        console.log(`✅ DEBUG: Successfully extracted ${externalLinks.length} external links`);
        
        if (countElement) {
            countElement.textContent = `(Found ${externalLinks.length})`;
            countElement.style.color = '#10b981'; // Green to indicate success
        }
        
        table.innerHTML = externalLinks.map((link, index) => `
            <tr class="hover:bg-gray-50">
                <td class="px-4 py-2 text-sm">${index + 1}</td>
                <td class="px-4 py-2 text-sm text-blue-600">${link.url}</td>
                <td class="px-4 py-2 text-sm">${link.anchor}</td>
            </tr>
        `).join('');
    }

    extractInternalLinks(data) {
        console.log('🔍 Extracting internal links from data:', data);
        
        // Try different data paths to find the correct structure
        const dataPath1 = data?.analysis?.pages?.[0]; // API response path
        const dataPath2 = data?.pages?.[0]; // Direct analysis path
        const page = dataPath1 || dataPath2;
        
        if (!page) {
            console.log('❌ No page data found for internal links');
            return null;
        }
        
        console.log('📄 Page data for internal links:', page);
        
        let internalLinks = [];
        
        // 🎯 PRIORITY 1: Use structured internal_links array (enhanced extraction from page.py)
        if (page.internal_links && Array.isArray(page.internal_links)) {
            console.log('✅ Found structured internal_links array:', page.internal_links.length);
            internalLinks = page.internal_links.map(link => ({
                url: link.url || link,
                anchor: link.anchor_text || link.title || '[No anchor text]'
            }));
        }
        
        // 🎯 PRIORITY 2: Process generic links array and filter for internal
        else if (page.links && Array.isArray(page.links)) {
            console.log('⚡ Processing generic links array for internal links:', page.links.length);
            try {
                const baseUrl = new URL(page.url);
                internalLinks = page.links.filter(linkUrl => {
                    try {
                        if (typeof linkUrl === 'string') {
                            const testUrl = new URL(linkUrl, baseUrl);
                            return testUrl.hostname === baseUrl.hostname;
                        }
                        return false;
                    } catch {
                        return false;
                    }
                }).map(linkUrl => ({
                    url: linkUrl,
                    anchor: '[Extracted from links]'
                }));
            } catch (e) {
                console.log('❌ Error processing links for internal:', e);
            }
        }
        
        console.log(`🔗 Final internal links extracted: ${internalLinks.length}`);
        console.log('Internal links preview:', internalLinks.slice(0, 3));
        
        return internalLinks.length > 0 ? internalLinks : null;
    }

    extractExternalLinks(data) {
        console.log('🔍 Extracting external links from data:', data);
        
        // Try different data paths to find the correct structure
        const dataPath1 = data?.analysis?.pages?.[0]; // API response path
        const dataPath2 = data?.pages?.[0]; // Direct analysis path
        const page = dataPath1 || dataPath2;
        
        if (!page) {
            console.log('❌ No page data found for external links');
            return null;
        }
        
        console.log('📄 Page data for external links:', page);
        
        let externalLinks = [];
        
        // 🎯 PRIORITY 1: Use structured external_links array (enhanced extraction from page.py)
        if (page.external_links && Array.isArray(page.external_links)) {
            console.log('✅ Found structured external_links array:', page.external_links.length);
            externalLinks = page.external_links.map(link => ({
                url: link.url || link,
                anchor: link.anchor_text || link.title || '[No anchor text]'
            }));
        }
        
        // 🎯 PRIORITY 2: Process generic links array and filter for external
        else if (page.links && Array.isArray(page.links)) {
            console.log('⚡ Processing generic links array for external links:', page.links.length);
            try {
                const baseUrl = new URL(page.url);
                externalLinks = page.links.filter(linkUrl => {
                    try {
                        if (typeof linkUrl === 'string') {
                            const testUrl = new URL(linkUrl, baseUrl);
                            return testUrl.hostname !== baseUrl.hostname;
                        }
                        return false;
                    } catch {
                        return false;
                    }
                }).map(linkUrl => ({
                    url: linkUrl,
                    anchor: '[Extracted from links]'
                }));
            } catch (e) {
                console.log('❌ Error processing links for external:', e);
            }
        }
        
        console.log(`🔗 Final external links extracted: ${externalLinks.length}`);
        console.log('External links preview:', externalLinks.slice(0, 3));
        
        return externalLinks.length > 0 ? externalLinks : null;
    }

    extractLinksFromHTML(htmlContent, baseUrl, isInternal) {
        try {
            // Create a temporary DOM parser
            const parser = new DOMParser();
            const doc = parser.parseFromString(htmlContent, 'text/html');
            const links = [];
            
            // Extract all anchor tags
            const anchors = doc.querySelectorAll('a[href]');
            
            anchors.forEach(anchor => {
                try {
                    const href = anchor.getAttribute('href');
                    if (!href || href.startsWith('#') || href.startsWith('mailto:') || href.startsWith('tel:')) {
                        return; // Skip fragments, email and phone links
                    }
                    
                    // Resolve relative URLs
                    const fullUrl = new URL(href, baseUrl);
                    const isInternalLink = fullUrl.hostname === baseUrl.hostname;
                    
                    // Only include links based on the type requested
                    if (isInternal === isInternalLink) {
                        links.push({
                            href: fullUrl.href,
                            text: anchor.textContent?.trim() || '',
                            anchor: anchor.textContent?.trim() || '[No anchor text]',
                            title: anchor.getAttribute('title') || ''
                        });
                    }
                } catch (e) {
                    // Skip invalid URLs
                }
            });
            
            return links;
        } catch (error) {
            console.warn('Failed to parse HTML for link extraction:', error);
            return [];
        }
    }

    updateSEOStrategySection() {
        const container = document.getElementById('seoStrategyTasks');
        const countElement = document.getElementById('strategyTasksCount');
        
        if (!container) return;
        
        // 使用动态战略建议，如果没有则使用默认模板
        let strategies = [];
        
        if (this.currentAnalysis && this.currentAnalysis.strategic_recommendations) {
            // 使用来自API的智能战略建议
            strategies = this.currentAnalysis.strategic_recommendations;
        } else {
            // 回退到通用模板（如果没有分析数据）
            strategies = [
                {
                    category: 'Content Review',
                    strategy: 'Review your content to match audience needs',
                    action: 'Analyze current content performance and identify gaps',
                    priority: 'medium',
                    impact: 'medium',
                    effort: 'medium'
                },
                {
                    category: 'Competitive Analysis',
                    strategy: 'Compare your traffic and rankings to competitors',
                    action: 'Use SEO tools to benchmark against top competitors',
                    priority: 'medium',
                    impact: 'high',
                    effort: 'medium'
                },
                {
                    category: 'Link Building',
                    strategy: 'Analyze your backlinks and find gaps compared to competitors',
                    action: 'Audit backlink profile and identify link building opportunities',
                    priority: 'medium',
                    impact: 'high',
                    effort: 'high'
                },
                {
                    category: 'Technical SEO',
                    strategy: 'Ensure your site is fast, mobile-friendly, and easy to use',
                    action: 'Run technical audit and fix core web vitals issues',
                    priority: 'high',
                    impact: 'high',
                    effort: 'medium'
                }
            ];
        }
        
        if (countElement) {
            countElement.textContent = `${strategies.length} Strategies`;
        }
        
        // 更新策略显示
        this.renderStrategicRecommendations(strategies);
    }

    renderStrategicRecommendations(strategies) {
        const container = document.getElementById('seoStrategyTasks');
        if (!container) return;
        
        // 清除现有内容
        container.innerHTML = '';
        
        strategies.forEach((strategy, index) => {
            const priorityClass = this.getPriorityClass(strategy.priority || 'medium');
            const impactBadge = this.getImpactBadge(strategy.impact || 'medium');
            const effortBadge = this.getEffortBadge(strategy.effort || 'medium');
            
            const strategyElement = document.createElement('div');
            strategyElement.className = 'strategy-card p-4 border rounded-lg hover:shadow-md transition-all duration-200 mb-4';
            strategyElement.innerHTML = `
                <div class="flex items-start justify-between">
                    <div class="flex items-start flex-1">
                        <input type="checkbox" class="strategy-checkbox mr-4 mt-1 h-4 w-4 text-purple-600 rounded" 
                               data-strategy-index="${index}">
                        <div class="flex-1">
                            <div class="flex items-center mb-2">
                                <span class="strategy-category text-sm font-medium text-purple-600 mr-2">
                                    ${strategy.category || 'Strategy'}
                                </span>
                                <span class="priority-badge ${priorityClass}">${strategy.priority || 'medium'}</span>
                                ${impactBadge}
                                ${effortBadge}
                            </div>
                            <h4 class="strategy-title font-semibold text-gray-900 mb-2">
                                ${strategy.strategy || strategy.action || 'Strategic recommendation'}
                            </h4>
                            <p class="strategy-action text-sm text-gray-600 mb-3">
                                ${strategy.action || strategy.strategy || 'Implement this strategy for SEO improvement'}
                            </p>
                            <div class="strategy-links flex items-center space-x-4">
                                <button class="add-to-todo-btn text-purple-600 hover:text-purple-800 text-sm font-medium transition-colors"
                                        onclick="seoAgent.addStrategyToTodo(${index})">
                                    <i class="fas fa-plus mr-1"></i>Add to TODO
                                </button>
                                <button class="link-to-analysis-btn text-blue-600 hover:text-blue-800 text-sm font-medium transition-colors"
                                        onclick="seoAgent.linkToAnalysisSection('${strategy.category}')">
                                    <i class="fas fa-link mr-1"></i>View Details
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            container.appendChild(strategyElement);
        });
        
        // 添加策略复选框事件监听器
        this.bindStrategyCheckboxEvents();
    }

    getPriorityClass(priority) {
        switch (priority.toLowerCase()) {
            case 'critical': return 'bg-red-100 text-red-800 px-2 py-1 rounded text-xs font-medium';
            case 'high': return 'bg-orange-100 text-orange-800 px-2 py-1 rounded text-xs font-medium';
            case 'medium': return 'bg-yellow-100 text-yellow-800 px-2 py-1 rounded text-xs font-medium';
            case 'low': return 'bg-green-100 text-green-800 px-2 py-1 rounded text-xs font-medium';
            default: return 'bg-gray-100 text-gray-800 px-2 py-1 rounded text-xs font-medium';
        }
    }

    getImpactBadge(impact) {
        const impactColors = {
            'very_high': 'bg-purple-100 text-purple-800',
            'high': 'bg-blue-100 text-blue-800',
            'medium': 'bg-indigo-100 text-indigo-800',
            'low': 'bg-gray-100 text-gray-800'
        };
        const colorClass = impactColors[impact] || impactColors['medium'];
        return `<span class="${colorClass} px-2 py-1 rounded text-xs font-medium ml-1">Impact: ${impact.replace('_', ' ')}</span>`;
    }

    getEffortBadge(effort) {
        const effortColors = {
            'low': 'bg-green-100 text-green-800',
            'medium': 'bg-yellow-100 text-yellow-800',
            'high': 'bg-red-100 text-red-800'
        };
        const colorClass = effortColors[effort] || effortColors['medium'];
        return `<span class="${colorClass} px-2 py-1 rounded text-xs font-medium ml-1">Effort: ${effort}</span>`;
    }

    bindStrategyCheckboxEvents() {
        document.querySelectorAll('.strategy-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const strategyIndex = parseInt(e.target.dataset.strategyIndex);
                if (e.target.checked && this.currentAnalysis && this.currentAnalysis.strategic_recommendations) {
                    const strategy = this.currentAnalysis.strategic_recommendations[strategyIndex];
                    if (strategy) {
                        this.addTodoFromRecommendation(
                            `${strategy.category}: ${strategy.action || strategy.strategy}`, 
                            strategy.priority || 'medium'
                        );
                    }
                }
            });
        });
    }

    async addStrategyToTodo(strategyIndex) {
        if (this.currentAnalysis && this.currentAnalysis.strategic_recommendations) {
            const strategy = this.currentAnalysis.strategic_recommendations[strategyIndex];
            if (strategy) {
                try {
                    // Call the backend API to create TODO from strategy
                    const response = await fetch(`${this.apiBaseUrl}/todos/from-strategy`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            strategy: strategy
                        })
                    });

                    const result = await response.json();

                    if (result.success) {
                        // Also add to local storage for immediate UI update
                        this.addTodoFromRecommendation(
                            result.todo.text,
                            result.todo.priority
                        );
                        this.showAlert('Strategy added to TODO list!', 'success');
                    } else if (result.duplicate) {
                        this.showAlert(result.message, 'warning');
                    } else {
                        throw new Error(result.error || 'Failed to add strategy to TODO');
                    }
                } catch (error) {
                    console.error('Failed to add strategy to TODO:', error);
                    // Fallback to local storage if API fails
                    this.addTodoFromRecommendation(
                        `${strategy.category}: ${strategy.action || strategy.strategy}`, 
                        strategy.priority || 'medium'
                    );
                    this.showAlert('Strategy added to TODO list! (offline mode)', 'success');
                }
            }
        }
    }

    linkToAnalysisSection(category) {
        // Map strategy categories to analysis sections
        const categoryMappings = {
            'Content Review': 'basic-seo',
            'Content Strategy': 'basic-seo', 
            'Content Quality': 'basic-seo',
            'Competitive Analysis': 'ai-analysis',
            'Link Building': 'basic-seo',
            'Technical SEO': 'professional-diagnostics',
            'Performance': 'professional-diagnostics',
            'Mobile SEO': 'professional-diagnostics',
            'Security': 'professional-diagnostics',
            'Structured Data': 'professional-diagnostics',
            'Trends Analysis': 'ai-analysis',
            'Keyword Optimization': 'basic-seo',
            'User Experience': 'professional-diagnostics',
            'Analytics': 'ai-analysis'
        };

        // Get the target section ID
        const targetSection = categoryMappings[category] || 'basic-seo';
        
        // Show the target section
        this.showSection(targetSection);
        
        // Scroll to the section with smooth animation
        const element = document.getElementById(targetSection);
        if (element) {
            element.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
            });
            
            // Add a highlight effect
            element.style.border = '2px solid #8B5CF6';
            element.style.boxShadow = '0 0 20px rgba(139, 92, 246, 0.3)';
            element.style.transition = 'all 0.3s ease';
            
            // Remove highlight after 3 seconds
            setTimeout(() => {
                element.style.border = '';
                element.style.boxShadow = '';
                element.style.transition = '';
            }, 3000);
        }
        
        // Show success message
        this.showAlert(`Viewing details for ${category} in ${targetSection.replace('-', ' ')} section`, 'info');
    }

    async syncTodosWithBackend() {
        // 🔄 Sync local todos with backend API
        try {
            // Get todos from backend
            const response = await fetch(`${this.apiBaseUrl}/todos`, {
                method: 'GET'
            });

            if (response.ok) {
                const result = await response.json();
                
                // Merge backend todos with local todos
                const backendTodos = result.todos || [];
                const localTodos = this.todos;
                
                // Create a combined list, prioritizing backend data
                const mergedTodos = [...backendTodos];
                
                // Add local todos that don't exist in backend
                localTodos.forEach(localTodo => {
                    const existsInBackend = backendTodos.some(backendTodo => 
                        backendTodo.text === localTodo.text || backendTodo.id === localTodo.id
                    );
                    
                    if (!existsInBackend) {
                        mergedTodos.push(localTodo);
                    }
                });
                
                this.todos = mergedTodos;
                this.saveTodos();
                this.renderTodos();
                this.updateTodoStats();
                
                console.log(`🔄 Synced ${mergedTodos.length} todos with backend`);
            }
        } catch (error) {
            console.warn('Failed to sync todos with backend:', error);
            // Continue using local storage if backend sync fails
        }
    }

    async toggleTodo(id) {
        const todo = this.todos.find(t => t.id === id);
        if (!todo) return;

        const oldCompleted = todo.completed;
        todo.completed = !todo.completed;

        try {
            // Update backend first
            const response = await fetch(`${this.apiBaseUrl}/todos`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    id: id,
                    completed: todo.completed
                })
            });

            if (!response.ok) {
                throw new Error('Backend update failed');
            }

            // Update local storage and UI
            this.saveTodos();
            this.renderTodos();
            this.updateTodoStats();
        } catch (error) {
            console.warn('Failed to update todo on backend:', error);
            // Revert the change if backend update failed
            todo.completed = oldCompleted;
            
            // Still update local storage and UI for offline functionality
            this.saveTodos();
            this.renderTodos();
            this.updateTodoStats();
            
            this.showAlert('Todo updated locally (backend sync failed)', 'warning');
        }
    }

    async deleteTodo(id) {
        try {
            // Delete from backend first
            const response = await fetch(`${this.apiBaseUrl}/todos`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    id: id
                })
            });

            if (!response.ok) {
                throw new Error('Backend delete failed');
            }

            // Remove from local storage
            this.todos = this.todos.filter(t => t.id !== id);
            this.saveTodos();
            this.renderTodos();
            this.updateTodoStats();
        } catch (error) {
            console.warn('Failed to delete todo from backend:', error);
            
            // Still delete locally for offline functionality
            this.todos = this.todos.filter(t => t.id !== id);
            this.saveTodos();
            this.renderTodos();
            this.updateTodoStats();
            
            this.showAlert('Todo deleted locally (backend sync failed)', 'warning');
        }
    }

    async clearCompleted() {
        try {
            // Clear completed from backend
            const response = await fetch(`${this.apiBaseUrl}/todos/clear-completed`, {
                method: 'POST'
            });

            if (response.ok) {
                const result = await response.json();
                this.showAlert(`Cleared ${result.cleared_count} completed todos`, 'success');
            }

            // Also clear locally
            this.todos = this.todos.filter(t => !t.completed);
            this.saveTodos();
            this.renderTodos();
            this.updateTodoStats();
        } catch (error) {
            console.warn('Failed to clear completed todos from backend:', error);
            
            // Still clear locally
            this.todos = this.todos.filter(t => !t.completed);
            this.saveTodos();
            this.renderTodos();
            this.updateTodoStats();
            
            this.showAlert('Completed todos cleared locally', 'warning');
        }
    }

    renderTodos() {
        const container = document.getElementById('todoList');
        if (!container) return;
        
        if (this.todos.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center py-8">No SEO tasks</p>';
            return;
        }
        
        const sortedTodos = this.todos.sort((a, b) => {
            if (a.completed !== b.completed) {
                return a.completed ? 1 : -1;
            }
            const priorityOrder = { high: 0, medium: 1, low: 2 };
            return priorityOrder[a.priority] - priorityOrder[b.priority];
        });
        
        container.innerHTML = sortedTodos.map(todo => `
            <div class="todo-item flex items-center p-3 border rounded-lg ${todo.completed ? 'bg-gray-50 opacity-75' : 'bg-white'}">
                <input type="checkbox" ${todo.completed ? 'checked' : ''} 
                       onchange="seoAgent.toggleTodo(${todo.id})" 
                       class="mr-3 h-4 w-4 text-indigo-600 rounded">
                <div class="flex-1">
                    <span class="${todo.completed ? 'line-through text-gray-500' : 'text-gray-900'}">${todo.text}</span>
                    <div class="text-xs text-gray-500 mt-1">
                        <span class="priority-badge priority-${todo.priority} px-2 py-1 rounded mr-2">
                            ${todo.priority === 'high' ? 'High' : todo.priority === 'medium' ? 'Medium' : 'Low'}
                        </span>
                        ${new Date(todo.createdAt).toLocaleDateString()}
                    </div>
                </div>
                <button onclick="seoAgent.deleteTodo(${todo.id})" 
                        class="text-red-500 hover:text-red-700 ml-2">
                    <i class="fas fa-trash text-sm"></i>
                </button>
            </div>
        `).join('');
    }

    updateTodoStats() {
        const statsElement = document.getElementById('todoStats');
        if (statsElement) {
            const remaining = this.todos.filter(t => !t.completed).length;
            statsElement.textContent = `${remaining} pending tasks`;
        }
    }

    saveTodos() {
        localStorage.setItem('seoTodos', JSON.stringify(this.todos));
    }

    showLoading(show) {
        const loadingElement = document.getElementById('loadingIndicator');
        const analyzeBtn = document.getElementById('analyzeBtn');
        
        if (loadingElement) {
            if (show) {
                loadingElement.classList.remove('hidden');
            } else {
                loadingElement.classList.add('hidden');
            }
        }
        
        if (analyzeBtn) {
            analyzeBtn.disabled = show;
            analyzeBtn.innerHTML = show ? 
                '<i class="fas fa-rocket fa-spin mr-2"></i>Analyzing...' : 
                '<i class="fas fa-rocket mr-2"></i>Analyze Now';
        }
    }

    async checkApiHealth() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/health`, {
                method: 'GET'
            });
            
            if (!response.ok) {
                console.warn('API health check failed:', response.status);
            }
        } catch (error) {
            console.warn('API health check failed:', error);
            // Don't show alert on page load, just log the warning
        }
    }

    async generateSitemap() {
        const urlInput = document.getElementById('urlInput');
        const url = urlInput?.value?.trim();
        
        if (!url) {
            this.showAlert('Please enter a valid website URL first', 'warning');
            return;
        }

        const generateBtn = document.getElementById('generateSitemapBtn');
        const statusDiv = document.getElementById('sitemapStatus');
        const resultsDiv = document.getElementById('sitemapResults');
        const statusText = document.getElementById('sitemapStatusText');
        const progress = document.getElementById('sitemapProgress');
        
        // Hide results and show status
        resultsDiv?.classList.add('hidden');
        statusDiv?.classList.remove('hidden');
        
        // Disable button and show loading state
        if (generateBtn) {
            generateBtn.disabled = true;
            generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i><span>Generating...</span>';
        }
        
        try {
            // Progress simulation for better UX
            const progressSteps = [
                { text: 'Crawling website...', progress: 25 },
                { text: 'Discovering URLs...', progress: 50 },
                { text: 'Analyzing page structure...', progress: 75 },
                { text: 'Generating XML sitemap...', progress: 90 },
                { text: 'Validating sitemap...', progress: 100 }
            ];
            
            let stepIndex = 0;
            const updateProgress = () => {
                if (stepIndex < progressSteps.length) {
                    const step = progressSteps[stepIndex];
                    if (statusText) statusText.textContent = step.text;
                    if (progress) progress.style.width = `${step.progress}%`;
                    stepIndex++;
                }
            };
            
            // Start progress updates
            updateProgress();
            const progressInterval = setInterval(updateProgress, 800);
            
            const response = await fetch(`${this.apiBaseUrl}/generate-sitemap`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            });

            clearInterval(progressInterval);
            
            if (!response.ok) {
                let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
                try {
                    const errorData = await response.json();
                    if (errorData.error) {
                        errorMessage = errorData.error;
                    }
                } catch (e) {
                    // If we can't parse the error response, use the status text
                }
                throw new Error(errorMessage);
            }

            const result = await response.json();
            
            if (result.error) {
                throw new Error(result.error);
            }
            
            // Hide status and show results
            statusDiv?.classList.add('hidden');
            resultsDiv?.classList.remove('hidden');
            
            // Update results
            const urlCount = document.getElementById('urlCount');
            const fileSize = document.getElementById('fileSize');
            const generationTime = document.getElementById('generationTime');
            
            if (urlCount) urlCount.textContent = result.validation?.url_count || 'Unknown';
            if (fileSize) fileSize.textContent = Math.round((result.validation?.size_bytes || 0) / 1024);
            if (generationTime) generationTime.textContent = result.performance?.execution_time || 'Unknown';
            
            // Create download functionality
            if (result.sitemap_xml) {
                this.createSitemapDownload(result.sitemap_xml, result.website_url);
            }
            
            this.showAlert('🎉 Sitemap generated successfully! Click to download.', 'success');
            
        } catch (error) {
            console.error('Sitemap generation failed:', error);
            statusDiv?.classList.add('hidden');
            
            let errorMessage = 'Sitemap generation failed';
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                errorMessage = 'Cannot connect to SEO analyzer API. Please ensure the server is running.';
            } else if (error.message) {
                errorMessage = `Sitemap generation failed: ${error.message}`;
            }
            
            this.showAlert(errorMessage, 'error');
        } finally {
            // Reset button state
            if (generateBtn) {
                generateBtn.disabled = false;
                generateBtn.innerHTML = '<i class="fas fa-download mr-2"></i><span>Generate & Download Sitemap</span>';
            }
        }
    }

    createSitemapDownload(sitemapXml, websiteUrl) {
        // Create download link
        const blob = new Blob([sitemapXml], { type: 'application/xml' });
        const downloadUrl = URL.createObjectURL(blob);
        
        // Add download button to results section
        const resultsDiv = document.getElementById('sitemapResults');
        if (resultsDiv) {
            const existingDownload = resultsDiv.querySelector('.download-btn');
            if (existingDownload) {
                existingDownload.remove();
            }
            
            const downloadBtn = document.createElement('div');
            downloadBtn.className = 'download-btn mt-3';
            downloadBtn.innerHTML = `
                <button type="button" 
                        class="w-full bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center justify-center">
                    <i class="fas fa-download mr-2"></i>
                    Download sitemap.xml
                </button>
            `;
            
            const downloadButton = downloadBtn.querySelector('button');
            downloadButton.addEventListener('click', () => {
                try {
                    const link = document.createElement('a');
                    link.href = downloadUrl;
                    link.download = 'sitemap.xml';
                    link.style.display = 'none';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    
                    this.showAlert('✅ Sitemap downloaded successfully! Upload it to your website root directory.', 'success');
                } catch (error) {
                    console.error('Download failed:', error);
                    this.showAlert('❌ Download failed. Please try again or check your browser settings.', 'error');
                }
            });
            
            resultsDiv.appendChild(downloadBtn);
        }
        
        // Auto-download option
        setTimeout(() => {
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.download = 'sitemap.xml';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            // Cleanup blob URL
            setTimeout(() => URL.revokeObjectURL(downloadUrl), 1000);
        }, 500);
    }

    async downloadReport() {
        if (!this.currentAnalysis) {
            this.showAlert('Please run an SEO analysis first before downloading a report', 'warning');
            return;
        }

        const urlInput = document.getElementById('urlInput');
        const url = urlInput?.value?.trim();
        const formatSelect = document.getElementById('reportFormat');
        const format = formatSelect?.value || 'html';

        if (!url) {
            this.showAlert('Please enter a valid website URL first', 'warning');
            return;
        }

        const downloadBtn = document.getElementById('downloadReportBtn');
        const statusDiv = document.getElementById('reportStatus');
        const resultsDiv = document.getElementById('reportResults');
        const statusText = document.getElementById('reportStatusText');
        const progress = document.getElementById('reportProgress');

        // Hide results and show status
        resultsDiv?.classList.add('hidden');
        statusDiv?.classList.remove('hidden');

        // Disable button and show loading state
        if (downloadBtn) {
            downloadBtn.disabled = true;
            downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i><span>Generating...</span>';
        }

        try {
            // Progress simulation for better UX
            const progressSteps = [
                { text: 'Consolidating analysis data...', progress: 25 },
                { text: 'Calculating comprehensive metrics...', progress: 50 },
                { text: 'Generating professional report...', progress: 75 },
                { text: 'Preparing download...', progress: 90 },
                { text: 'Report ready!', progress: 100 }
            ];

            let stepIndex = 0;
            const updateProgress = () => {
                if (stepIndex < progressSteps.length) {
                    const step = progressSteps[stepIndex];
                    if (statusText) statusText.textContent = step.text;
                    if (progress) progress.style.width = `${step.progress}%`;
                    stepIndex++;
                }
            };

            // Start progress updates
            updateProgress();
            const progressInterval = setInterval(updateProgress, 600);

            // Prepare analysis data for report generation
            const reportData = {
                url: url,
                format: format,
                analysis_data: {
                    url: url,
                    basic_seo_analysis: this.currentAnalysis.analysis?.pages?.[0] || {},
                    llm_analysis: this.currentAnalysis.analysis?.llm_analysis || {},
                    seo_score: this.currentAnalysis.seo_score || {},
                    recommendations: this.currentAnalysis.recommendations || [],
                    timestamp: new Date().toISOString()
                }
            };

            const response = await fetch(`${this.apiBaseUrl}/generate-report`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(reportData)
            });

            clearInterval(progressInterval);

            if (!response.ok) {
                let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
                try {
                    const errorData = await response.json();
                    if (errorData.error) {
                        errorMessage = errorData.error;
                    }
                } catch (e) {
                    // If we can't parse the error response, use the status text
                }
                throw new Error(errorMessage);
            }

            // Create download from response
            const blob = await response.blob();
            const filename = response.headers.get('Content-Disposition') 
                ? response.headers.get('Content-Disposition').split('filename=')[1]?.replace(/"/g, '')
                : `seo-report-${format}.${format === 'html' ? 'html' : format}`;
            
            const generationTime = response.headers.get('X-Generation-Time') || 'Unknown';
            const reportFormat = response.headers.get('X-Report-Format') || format;

            // Hide status and show results
            statusDiv?.classList.add('hidden');
            resultsDiv?.classList.remove('hidden');

            // Update results
            const reportFormatType = document.getElementById('reportFormatType');
            const reportFileSize = document.getElementById('reportFileSize');
            const reportGenerationTime = document.getElementById('reportGenerationTime');

            if (reportFormatType) reportFormatType.textContent = reportFormat.toUpperCase();
            if (reportFileSize) reportFileSize.textContent = Math.round(blob.size / 1024);
            if (reportGenerationTime) reportGenerationTime.textContent = generationTime;

            // Create and trigger download
            const downloadUrl = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.download = filename;
            link.style.display = 'none';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            // Cleanup blob URL
            setTimeout(() => URL.revokeObjectURL(downloadUrl), 1000);

            this.showAlert(`🎉 SEO Report downloaded successfully! Format: ${reportFormat.toUpperCase()}`, 'success');

        } catch (error) {
            console.error('Report generation failed:', error);
            statusDiv?.classList.add('hidden');

            let errorMessage = 'Report generation failed';
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                errorMessage = 'Cannot connect to SEO analyzer API. Please ensure the server is running.';
            } else if (error.message) {
                errorMessage = `Report generation failed: ${error.message}`;
            }

            this.showAlert(errorMessage, 'error');
        } finally {
            // Reset button state
            if (downloadBtn) {
                downloadBtn.disabled = false;
                downloadBtn.innerHTML = '<i class="fas fa-download mr-2"></i><span>Download SEO Report</span>';
            }
        }
    }

    showAlert(message, type = 'info') {
        // Remove any existing alerts first
        const existingAlerts = document.querySelectorAll('.seo-alert');
        existingAlerts.forEach(alert => {
            alert.style.transform = 'translateX(400px)';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        });
        
        const alert = document.createElement('div');
        alert.className = `seo-alert fixed top-6 right-6 p-4 rounded-lg shadow-lg z-50 alert-${type} max-w-sm`;
        
        // Professional styling based on type
        let icon = 'fa-info-circle';
        let bgColor = 'linear-gradient(135deg, rgba(59, 130, 246, 0.9) 0%, rgba(37, 99, 235, 0.9) 100%)';
        let borderColor = '#3b82f6';
        
        switch (type) {
            case 'success':
                icon = 'fa-check-circle';
                bgColor = 'linear-gradient(135deg, rgba(16, 185, 129, 0.9) 0%, rgba(5, 150, 105, 0.9) 100%)';
                borderColor = '#10b981';
                break;
            case 'error':
                icon = 'fa-exclamation-circle';
                bgColor = 'linear-gradient(135deg, rgba(239, 68, 68, 0.9) 0%, rgba(220, 38, 38, 0.9) 100%)';
                borderColor = '#ef4444';
                break;
            case 'warning':
                icon = 'fa-exclamation-triangle';
                bgColor = 'linear-gradient(135deg, rgba(245, 158, 11, 0.9) 0%, rgba(217, 119, 6, 0.9) 100%)';
                borderColor = '#f59e0b';
                break;
        }
        
        alert.style.background = bgColor;
        alert.style.backdropFilter = 'blur(10px)';
        alert.style.border = `1px solid ${borderColor}`;
        alert.style.color = 'white';
        alert.style.fontWeight = '500';
        alert.style.transform = 'translateX(400px)';
        alert.style.opacity = '0';
        alert.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        
        alert.innerHTML = `
            <div class="flex items-center">
                <i class="fas ${icon} mr-3 text-lg"></i>
                <div class="flex-1">
                    <span class="text-sm">${message}</span>
                </div>
                <button onclick="this.parentElement.parentElement.style.transform='translateX(400px)'; this.parentElement.parentElement.style.opacity='0'; setTimeout(() => this.parentElement.parentElement.remove(), 300);" 
                        class="ml-4 text-white hover:text-gray-200 transition-colors">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(alert);
        
        // Professional slide-in animation
        setTimeout(() => {
            alert.style.transform = 'translateX(0)';
            alert.style.opacity = '1';
        }, 100);
        
        // Add subtle bounce effect
        setTimeout(() => {
            alert.style.transform = 'translateX(-8px)';
            setTimeout(() => {
                alert.style.transform = 'translateX(0)';
            }, 150);
        }, 400);
        
        // Auto-dismiss with fade out
        setTimeout(() => {
            if (alert.parentElement) {
                alert.style.transform = 'translateX(400px)';
                alert.style.opacity = '0';
                setTimeout(() => {
                    if (alert.parentElement) {
                        alert.remove();
                    }
                }, 300);
            }
        }, type === 'success' ? 4000 : 5000);
        
        // Add click to dismiss
        alert.addEventListener('click', () => {
            alert.style.transform = 'translateX(400px)';
            alert.style.opacity = '0';
            setTimeout(() => {
                if (alert.parentElement) {
                    alert.remove();
                }
            }, 300);
        });
    }
}

// Global functions
function toggleTheme() {
    if (window.seoAgent) {
        window.seoAgent.toggleTheme();
    } else {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    }
}

function showSection(sectionId) {
    if (window.seoAgent) {
        window.seoAgent.showSection(sectionId);
    }
}

function closeModal() {
    const modal = document.getElementById('pageModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function refreshAnalysis() {
    if (window.seoAgent) {
        window.seoAgent.analyzeWebsite();
    }
}

function exportResults() {
    if (window.seoAgent && window.seoAgent.currentAnalysis) {
        const dataStr = JSON.stringify(window.seoAgent.currentAnalysis, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'seo-analysis.json';
        link.click();
        URL.revokeObjectURL(url);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.seoAgent = new SEOAgent();
    
    // Add dynamic styles
    const style = document.createElement('style');
    style.textContent = `
        .loading-step {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            font-size: 0.75rem;
            transition: all var(--transition-base);
        }
        
        .loading-step.active .status-indicator {
            animation: pulse-processing 1.5s infinite;
        }
        
        .loading-step span {
            color: var(--gray-600);
            font-weight: 500;
        }
        
        .loading-step.active span {
            color: var(--primary-600);
            font-weight: 600;
        }
    `;
    document.head.appendChild(style);
});

// Professional Chart Functionality
class SEOChartManager {
    constructor() {
        this.charts = {};
        this.initializeCharts();
    }

    initializeCharts() {
        // Initialize all charts when data is available
        if (typeof Chart !== 'undefined') {
            Chart.defaults.responsive = true;
            Chart.defaults.maintainAspectRatio = false;
            Chart.defaults.plugins.legend.display = true;
            Chart.defaults.plugins.tooltip.enabled = true;
        }
    }

    createKeywordDensityChart(keywords) {
        const canvas = document.getElementById('keywordDensityChart');
        if (!canvas) {
            console.warn('Keyword chart canvas not found');
            return;
        }

        if (!keywords || keywords.length === 0) {
            console.warn('No keywords data for chart');
            this.createPlaceholderChart('keywordDensityChart', 'No keywords data available');
            return;
        }

        // Destroy existing chart
        if (this.charts.keywordDensity) {
            this.charts.keywordDensity.destroy();
        }

        // Take top 10 keywords and ensure they have valid data
        const topKeywords = keywords.slice(0, 10).filter(k => 
            k && (k.word || k.keyword) && (k.count || k.frequency || k.repeats || 0) > 0
        );

        if (topKeywords.length === 0) {
            this.createPlaceholderChart('keywordDensityChart', 'No valid keywords found');
            return;
        }

        const ctx = canvas.getContext('2d');

        this.charts.keywordDensity = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: topKeywords.map(k => k.word || k.keyword || 'Unknown'),
                datasets: [{
                    label: 'Keyword Frequency',
                    data: topKeywords.map(k => k.count || k.frequency || k.repeats || 0),
                    backgroundColor: 'rgba(59, 130, 246, 0.8)',
                    borderColor: 'rgba(59, 130, 246, 1)',
                    borderWidth: 1,
                    borderRadius: 4,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: `Top ${topKeywords.length} Keywords by Frequency`,
                        font: { size: 14, weight: 'bold' }
                    },
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Frequency'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Keywords'
                        },
                        ticks: {
                            maxRotation: 45,
                            minRotation: 0
                        }
                    }
                }
            }
        });

        console.log('✅ Keyword density chart created successfully with', topKeywords.length, 'keywords');
    }

    createCategoryScoresChart(categoryScores) {
        const canvas = document.getElementById('categoryScoresChart');
        if (!canvas) {
            console.warn('Category scores chart canvas not found');
            return;
        }

        if (!categoryScores || Object.keys(categoryScores).length === 0) {
            console.warn('No category scores data for chart');
            this.createPlaceholderChart('categoryScoresChart', 'Category scores not available');
            return;
        }

        if (this.charts.categoryScores) {
            this.charts.categoryScores.destroy();
        }

        const categories = Object.keys(categoryScores);
        const scores = categories.map(cat => {
            const score = categoryScores[cat];
            return typeof score === 'object' ? (score.score || 0) : (score || 0);
        }).filter(score => !isNaN(score));

        if (scores.length === 0) {
            this.createPlaceholderChart('categoryScoresChart', 'No valid category scores found');
            return;
        }

        const ctx = canvas.getContext('2d');
        this.charts.categoryScores = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: categories.map(cat => cat.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())),
                datasets: [{
                    label: 'SEO Category Scores',
                    data: scores,
                    borderColor: 'rgba(139, 92, 246, 1)',
                    backgroundColor: 'rgba(139, 92, 246, 0.2)',
                    pointBackgroundColor: 'rgba(139, 92, 246, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(139, 92, 246, 1)',
                    borderWidth: 2,
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'SEO Category Performance',
                        font: { size: 14, weight: 'bold' }
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            stepSize: 20,
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });

        console.log('✅ Category scores chart created successfully with', categories.length, 'categories');
    }

    createIssuesPriorityChart(issues) {
        const canvas = document.getElementById('issuesPriorityChart');
        if (!canvas) {
            console.warn('Issues priority chart canvas not found');
            return;
        }

        if (!issues) {
            console.warn('No issues data for chart');
            this.createPlaceholderChart('issuesPriorityChart', 'Issues data not available');
            return;
        }

        if (this.charts.issuesPriority) {
            this.charts.issuesPriority.destroy();
        }

        // Count issues by priority - handle both array and summary object
        const priorityCounts = {
            critical: 0,
            high: 0,
            medium: 0,
            low: 0
        };

        if (Array.isArray(issues)) {
            // Handle array of issues
            issues.forEach(issue => {
                const priority = issue.priority?.toLowerCase() || 'medium';
                if (priorityCounts.hasOwnProperty(priority)) {
                    priorityCounts[priority]++;
                }
            });
        } else if (typeof issues === 'object') {
            // Handle issues summary object
            priorityCounts.critical = issues.critical || 0;
            priorityCounts.high = issues.high || 0;
            priorityCounts.medium = issues.medium || 0;
            priorityCounts.low = issues.low || 0;
        }

        const totalIssues = Object.values(priorityCounts).reduce((a, b) => a + b, 0);
        if (totalIssues === 0) {
            this.createPlaceholderChart('issuesPriorityChart', 'No issues found - Great job!');
            return;
        }

        const ctx = canvas.getContext('2d');
        this.charts.issuesPriority = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Critical', 'High', 'Medium', 'Low'],
                datasets: [{
                    data: [
                        priorityCounts.critical,
                        priorityCounts.high,
                        priorityCounts.medium,
                        priorityCounts.low
                    ],
                    backgroundColor: [
                        'rgba(239, 68, 68, 0.8)',   // Critical - Red
                        'rgba(245, 158, 11, 0.8)',  // High - Orange
                        'rgba(59, 130, 246, 0.8)',  // Medium - Blue
                        'rgba(16, 185, 129, 0.8)'   // Low - Green
                    ],
                    borderColor: [
                        'rgba(239, 68, 68, 1)',
                        'rgba(245, 158, 11, 1)',
                        'rgba(59, 130, 246, 1)',
                        'rgba(16, 185, 129, 1)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: `Issues by Priority (${totalIssues} total)`,
                        font: { size: 14, weight: 'bold' }
                    },
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });

        console.log('✅ Issues priority chart created successfully with', totalIssues, 'total issues');
    }

    createPlaceholderChart(canvasId, message) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        // Destroy existing chart
        if (this.charts[canvasId.replace('Chart', '')]) {
            this.charts[canvasId.replace('Chart', '')].destroy();
        }

        const ctx = canvas.getContext('2d');
        this.charts[canvasId.replace('Chart', '')] = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Placeholder'],
                datasets: [{
                    data: [1],
                    backgroundColor: ['rgba(156, 163, 175, 0.3)'],
                    borderColor: ['rgba(156, 163, 175, 0.6)'],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: message,
                        font: { size: 14, weight: 'bold' },
                        color: 'rgba(107, 114, 128, 1)'
                    },
                    legend: {
                        display: false
                    },
                    tooltip: {
                        enabled: false
                    }
                }
            }
        });

        console.log('📊 Placeholder chart created for', canvasId, 'with message:', message);
    }

    updateChartsWithAnalysis(analysis) {
        if (!analysis) {
            console.warn('Chart Update: No analysis data provided');
            return;
        }

        console.log('=== Chart Data Debug Info ===');
        console.log('Full Analysis Object:', analysis);
        console.log('Analysis.analysis:', analysis.analysis);
        console.log('Analysis.keywords:', analysis.keywords);

        // Extract keywords from multiple possible sources
        const keywords = analysis.keywords || 
                         analysis.analysis?.keywords || 
                         analysis.pages?.[0]?.keywords || 
                         analysis.analysis?.pages?.[0]?.keywords ||
                         [];

        console.log('Extracted Keywords:', keywords);

        if (keywords.length > 0) {
            console.log('✅ Creating keyword density chart with', keywords.length, 'keywords');
            this.createKeywordDensityChart(keywords);
        } else {
            console.warn('⚠️ No keywords found for chart');
            // Create a placeholder chart
            this.createPlaceholderChart('keywordDensityChart', 'No keywords data available yet');
        }

        // Extract professional analysis from multiple possible sources
        const professionalAnalysis = analysis.analysis?.pages?.[0]?.professional_analysis ||
                                    analysis.pages?.[0]?.professional_analysis ||
                                    analysis.professional_analysis;

        console.log('Professional Analysis Found:', professionalAnalysis);

        if (professionalAnalysis) {
            // Category scores chart
            if (professionalAnalysis.category_scores) {
                console.log('✅ Creating category scores chart');
                console.log('Category Scores Data:', professionalAnalysis.category_scores);
                this.createCategoryScoresChart(professionalAnalysis.category_scores);
            } else {
                console.warn('⚠️ No category scores found');
                this.createPlaceholderChart('categoryScoresChart', 'Professional analysis in progress...');
            }

            // Issues priority chart
            if (professionalAnalysis.all_issues || professionalAnalysis.issues_summary) {
                console.log('✅ Creating issues priority chart');
                console.log('Issues Data:', professionalAnalysis.all_issues || professionalAnalysis.issues_summary);
                this.createIssuesPriorityChart(professionalAnalysis.all_issues || professionalAnalysis.issues_summary);
            } else {
                console.warn('⚠️ No issues data found');
                this.createPlaceholderChart('issuesPriorityChart', 'Issues analysis in progress...');
            }
        } else {
            console.warn('⚠️ No professional analysis data found');
            this.createPlaceholderChart('categoryScoresChart', 'Professional analysis not available');
            this.createPlaceholderChart('issuesPriorityChart', 'Issues analysis not available');
        }

        console.log('=== End Chart Data Debug ===');
    }

    destroyAllCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        this.charts = {};
    }
}

// Analysis Timing Manager to investigate timing inconsistencies
class AnalysisTimingManager {
    constructor() {
        this.analysisStartTime = null;
        this.analysisEndTime = null;
        this.phaseTimings = {};
        this.qualityMetrics = {};
        this.timingThresholds = {
            minimum_expected_time: 3000,  // 3 seconds minimum for thorough analysis
            maximum_reasonable_time: 60000, // 60 seconds maximum
            warning_quick_completion: 5000   // Warn if analysis completes under 5 seconds
        };
        this.init();
    }

    init() {
        console.log('🕐 AnalysisTimingManager initialized');
        this.bindAnalysisEvents();
    }

    bindAnalysisEvents() {
        // Hook into the existing analyzeWebsite method
        const originalAnalyze = window.seoAgent?.analyzeWebsite;
        if (originalAnalyze && window.seoAgent) {
            window.seoAgent.analyzeWebsite = async function() {
                const urlInput = document.getElementById('urlInput');
                const url = urlInput?.value?.trim() || 'unknown';
                window.analysisTimingManager.startAnalysis(url);
                try {
                    const result = await originalAnalyze.call(this);
                    window.analysisTimingManager.endAnalysis(this.currentAnalysis);
                    return result;
                } catch (error) {
                    window.analysisTimingManager.handleAnalysisError(error);
                    throw error;
                }
            };
        }
    }

    getUrlFromInput() {
        return document.getElementById('urlInput')?.value?.trim() || 'unknown';
    }

    startAnalysis(url) {
        this.analysisStartTime = Date.now();
        this.currentUrl = url;
        this.phaseTimings = {};
        this.qualityMetrics = {};
        
        console.log(`🚀 Analysis started for: ${url} at ${new Date().toISOString()}`);
        
        // Track phase start
        this.markPhaseStart('total_analysis');
        this.markPhaseStart('initial_request');
    }

    markPhaseStart(phaseName) {
        this.phaseTimings[phaseName] = { start: Date.now() };
        console.log(`📋 Phase started: ${phaseName}`);
    }

    markPhaseEnd(phaseName) {
        if (this.phaseTimings[phaseName]) {
            this.phaseTimings[phaseName].end = Date.now();
            this.phaseTimings[phaseName].duration = this.phaseTimings[phaseName].end - this.phaseTimings[phaseName].start;
            console.log(`✅ Phase completed: ${phaseName} (${this.phaseTimings[phaseName].duration}ms)`);
        }
    }

    endAnalysis(analysisResult) {
        this.analysisEndTime = Date.now();
        this.markPhaseEnd('total_analysis');
        
        const totalDuration = this.analysisEndTime - this.analysisStartTime;
        console.log(`🏁 Analysis completed for: ${this.currentUrl} in ${totalDuration}ms`);
        
        // Analyze quality and timing
        this.analyzeQuality(analysisResult, totalDuration);
        this.provideTimingFeedback(totalDuration);
        this.logDetailedReport();
    }

    analyzeQuality(analysisResult, duration) {
        this.qualityMetrics = {
            url: this.currentUrl,
            duration: duration,
            has_professional_analysis: !!(analysisResult?.analysis?.pages?.[0]?.professional_analysis),
            has_llm_analysis: !!(analysisResult?.analysis?.llm_analysis),
            has_keywords: !!(analysisResult?.keywords && analysisResult.keywords.length > 0),
            has_links: !!(analysisResult?.pages?.[0]?.links && analysisResult.pages[0].links.length > 0),
            pages_analyzed: analysisResult?.pages?.length || 0,
            seo_score_source: this.determineSEOScoreSource(analysisResult),
            completion_type: this.determineCompletionType(duration, analysisResult)
        };

        // Quality scoring
        let qualityScore = 0;
        if (this.qualityMetrics.has_professional_analysis) qualityScore += 30;
        if (this.qualityMetrics.has_llm_analysis) qualityScore += 25;
        if (this.qualityMetrics.has_keywords) qualityScore += 20;
        if (this.qualityMetrics.has_links) qualityScore += 15;
        if (this.qualityMetrics.pages_analyzed > 0) qualityScore += 10;

        this.qualityMetrics.quality_score = qualityScore;
        this.qualityMetrics.quality_grade = this.getQualityGrade(qualityScore);

        console.log('📊 Quality Analysis:', this.qualityMetrics);
    }

    determineSEOScoreSource(analysisResult) {
        if (analysisResult?.analysis?.pages?.[0]?.professional_analysis?.overall_score) {
            return 'professional_analysis';
        } else if (analysisResult?.seo_score) {
            return 'backend_calculation';
        } else {
            return 'frontend_fallback';
        }
    }

    determineCompletionType(duration, analysisResult) {
        if (duration < this.timingThresholds.warning_quick_completion) {
            if (this.qualityMetrics.has_professional_analysis && this.qualityMetrics.has_llm_analysis) {
                return 'fast_but_complete';
            } else {
                return 'suspiciously_fast';
            }
        } else if (duration > this.timingThresholds.maximum_reasonable_time) {
            return 'unusually_slow';
        } else {
            return 'normal';
        }
    }

    getQualityGrade(score) {
        if (score >= 90) return 'A+ (Excellent)';
        if (score >= 80) return 'A (Very Good)';
        if (score >= 70) return 'B (Good)';
        if (score >= 60) return 'C (Fair)';
        if (score >= 50) return 'D (Poor)';
        return 'F (Incomplete)';
    }

    provideTimingFeedback(duration) {
        let message = '';
        let type = 'info';

        switch (this.qualityMetrics.completion_type) {
            case 'suspiciously_fast':
                message = `⚠️ Analysis completed unusually quickly (${duration}ms). This may indicate:\n• Cached results being returned\n• Limited analysis depth\n• Network/server issues\n• Missing professional analysis components`;
                type = 'warning';
                break;
            case 'fast_but_complete':
                message = `✅ Excellent! Analysis completed quickly (${duration}ms) with comprehensive results including professional analysis and LLM insights.`;
                type = 'success';
                break;
            case 'unusually_slow':
                message = `🐌 Analysis took longer than expected (${duration}ms). This could be due to:\n• Complex website structure\n• LLM analysis processing time\n• Network latency\n• Server load`;
                type = 'warning';
                break;
            case 'normal':
                message = `✅ Analysis completed in normal timeframe (${duration}ms) with quality score: ${this.qualityMetrics.quality_grade}`;
                type = 'success';
                break;
        }

        if (window.seoAgent && message) {
            setTimeout(() => {
                window.seoAgent.showAlert(message, type);
            }, 1000);
        }
    }

    handleAnalysisError(error) {
        this.analysisEndTime = Date.now();
        const duration = this.analysisEndTime - this.analysisStartTime;
        
        console.error('❌ Analysis failed:', error);
        console.log(`💥 Analysis failed for: ${this.currentUrl} after ${duration}ms`);
        
        if (window.seoAgent) {
            window.seoAgent.showAlert(`Analysis failed after ${duration}ms. Error: ${error.message}`, 'error');
        }
    }

    logDetailedReport() {
        console.log('=== DETAILED TIMING ANALYSIS REPORT ===');
        console.log('URL:', this.currentUrl);
        console.log('Total Duration:', this.phaseTimings.total_analysis?.duration, 'ms');
        console.log('Quality Metrics:', this.qualityMetrics);
        console.log('Phase Timings:', this.phaseTimings);
        console.log('Completion Type:', this.qualityMetrics.completion_type);
        console.log('Quality Grade:', this.qualityMetrics.quality_grade);
        
        // Specific recommendations based on analysis
        if (this.qualityMetrics.completion_type === 'suspiciously_fast') {
            console.log('🔍 INVESTIGATION NEEDED:');
            console.log('• Check if professional analysis is enabled');
            console.log('• Verify LLM analysis is running');
            console.log('• Look for caching issues');
            console.log('• Compare with known good analyses');
        }
        
        console.log('=== END TIMING REPORT ===');
    }

    // Public method to compare two analyses
    compareAnalyses(analysis1, analysis2) {
        console.log('🔬 Comparing analyses:');
        console.log('Analysis 1:', analysis1);
        console.log('Analysis 2:', analysis2);
        
        const comparison = {
            duration_diff: Math.abs(analysis1.duration - analysis2.duration),
            quality_diff: Math.abs(analysis1.quality_score - analysis2.quality_score),
            features_comparison: {
                professional_analysis: [analysis1.has_professional_analysis, analysis2.has_professional_analysis],
                llm_analysis: [analysis1.has_llm_analysis, analysis2.has_llm_analysis],
                keywords: [analysis1.has_keywords, analysis2.has_keywords],
                links: [analysis1.has_links, analysis2.has_links]
            }
        };
        
        console.log('Comparison Results:', comparison);
        return comparison;
    }
}

// Initialize chart manager and integrate with SEO Agent
document.addEventListener('DOMContentLoaded', function() {
    // Initialize timing manager
    window.analysisTimingManager = new AnalysisTimingManager();
    
    // Add chart containers to professional diagnostics section if they don't exist
    const professionalSection = document.getElementById('professional-diagnostics');
    const categoryScores = document.getElementById('categoryScores');
    
    if (professionalSection && categoryScores && !document.getElementById('categoryScoresChart')) {
        // Create chart containers
        const chartSection = document.createElement('div');
        chartSection.className = 'grid grid-cols-1 md:grid-cols-2 gap-6 mb-6';
        chartSection.innerHTML = `
            <!-- Category Scores Chart -->
            <div class="bg-gray-50 rounded-lg p-4">
                <h4 class="text-lg font-semibold text-gray-800 mb-4">📊 Category Performance</h4>
                <div class="chart-container" style="height: 250px;">
                    <canvas id="categoryScoresChart"></canvas>
                </div>
            </div>
            
            <!-- Issues Priority Chart -->
            <div class="bg-gray-50 rounded-lg p-4">
                <h4 class="text-lg font-semibold text-gray-800 mb-4">🎯 Issues Breakdown</h4>
                <div class="chart-container" style="height: 250px;">
                    <canvas id="issuesPriorityChart"></canvas>
                </div>
            </div>
        `;
        
        // Insert chart section after category scores
        categoryScores.parentNode.insertBefore(chartSection, categoryScores.nextSibling);
    }
    
    // Wait for Chart.js to load
    if (typeof Chart !== 'undefined') {
        window.seoChartManager = new SEOChartManager();
        
        // Hook into existing SEO agent to update charts when analysis completes
        const originalUpdateDisplay = window.seoAgent?.updateSEOScoreDisplay;
        if (originalUpdateDisplay && window.seoAgent) {
            window.seoAgent.updateSEOScoreDisplay = function(data) {
                // Call original function
                originalUpdateDisplay.call(this, data);
                
                // Update charts with new data
                if (window.seoChartManager && this.currentAnalysis) {
                    setTimeout(() => {
                        window.seoChartManager.updateChartsWithAnalysis(this.currentAnalysis);
                    }, 500); // Small delay to ensure DOM is updated
                }
            };
        }
    }
});