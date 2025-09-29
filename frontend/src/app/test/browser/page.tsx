"use client"

import { useState, useEffect } from 'react'
import dynamic from 'next/dynamic'
import { browserTestSuite, BrowserTestResult } from '@/utils/browserTest'

// Dynamically import BrowserInfo to avoid SSR issues
const BrowserInfo = dynamic(() => import('@/components/debug/browser-info').then(mod => ({ default: mod.BrowserInfo })), {
  ssr: false,
  loading: () => <div>Loading browser info...</div>
})
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Play, Download, RefreshCw, CheckCircle, XCircle } from 'lucide-react'

export default function BrowserTestPage() {
  const [testResults, setTestResults] = useState<BrowserTestResult[]>([])
  const [isRunningTests, setIsRunningTests] = useState(false)
  const [testReport, setTestReport] = useState('')

  const runTests = async () => {
    setIsRunningTests(true)
    setTestResults([])
    
    try {
      const results = await browserTestSuite.runAllTests()
      setTestResults(results)
      
      const report = browserTestSuite.generateReport()
      setTestReport(report)
    } catch (error) {
      console.error('Error running tests:', error)
    } finally {
      setIsRunningTests(false)
    }
  }

  const downloadReport = () => {
    const blob = new Blob([testReport], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `browser-compatibility-report-${new Date().toISOString().split('T')[0]}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const passedTests = testResults.filter(r => r.passed).length
  const totalTests = testResults.length
  const successRate = totalTests > 0 ? (passedTests / totalTests) * 100 : 0

  return (
    <div className="container mx-auto py-8 space-y-8">
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold">Browser Compatibility Testing</h1>
        <p className="text-muted-foreground max-w-2xl mx-auto">
          Test and validate browser compatibility for the conversation simulator across different browsers and devices.
        </p>
      </div>

      {/* Browser Info Card */}
      <BrowserInfo showDetails={true} />

      {/* Test Controls */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Play className="h-5 w-5" />
            Test Suite
          </CardTitle>
          <CardDescription>
            Run comprehensive browser compatibility tests
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4">
            <Button 
              onClick={runTests} 
              disabled={isRunningTests}
              className="flex items-center gap-2"
            >
              {isRunningTests ? (
                <>
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  Running Tests...
                </>
              ) : (
                <>
                  <Play className="h-4 w-4" />
                  Run Tests
                </>
              )}
            </Button>
            
            {testResults.length > 0 && (
              <Button 
                variant="outline" 
                onClick={downloadReport}
                className="flex items-center gap-2"
              >
                <Download className="h-4 w-4" />
                Download Report
              </Button>
            )}
          </div>

          {/* Test Summary */}
          {testResults.length > 0 && (
            <div className="p-4 bg-muted rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium">Test Summary</span>
                <Badge variant={successRate >= 80 ? "default" : successRate >= 60 ? "secondary" : "destructive"}>
                  {successRate.toFixed(1)}% Pass Rate
                </Badge>
              </div>
              <div className="text-sm text-muted-foreground">
                {passedTests} of {totalTests} tests passed
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Test Results */}
      {testResults.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Test Results</CardTitle>
            <CardDescription>
              Detailed results from browser compatibility tests
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {testResults.map((result, index) => (
                <div 
                  key={index}
                  className="flex items-center justify-between p-3 border rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    {result.passed ? (
                      <CheckCircle className="h-5 w-5 text-green-600" />
                    ) : (
                      <XCircle className="h-5 w-5 text-red-600" />
                    )}
                    <div>
                      <div className="font-medium">{result.testName}</div>
                      <div className="text-sm text-muted-foreground">
                        {result.details}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-mono">{result.duration}ms</div>
                    <Badge variant={result.passed ? "default" : "destructive"} className="text-xs">
                      {result.passed ? "PASS" : "FAIL"}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Instructions */}
      <Card>
        <CardHeader>
          <CardTitle>Testing Instructions</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h4 className="font-medium mb-2">For Firefox Testing:</h4>
            <ul className="text-sm text-muted-foreground space-y-1 ml-4">
              <li>• Open Firefox and navigate to this page</li>
              <li>• Run the test suite and check for any compatibility issues</li>
              <li>• Pay attention to audio format support and performance metrics</li>
              <li>• Test the actual conversation interface for audio quality</li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-medium mb-2">For Safari Testing:</h4>
            <ul className="text-sm text-muted-foreground space-y-1 ml-4">
              <li>• Open Safari and navigate to this page</li>
              <li>• Run the test suite and check for WebKit-specific issues</li>
              <li>• Test audio playback and recording functionality</li>
              <li>• Verify WebSocket connections work properly</li>
            </ul>
          </div>

          <div>
            <h4 className="font-medium mb-2">What to Look For:</h4>
            <ul className="text-sm text-muted-foreground space-y-1 ml-4">
              <li>• Audio format compatibility (WebM vs MP4 vs WAV)</li>
              <li>• Performance differences in audio loading times</li>
              <li>• Voice Activity Detection accuracy</li>
              <li>• WebSocket connection stability</li>
              <li>• Memory usage patterns</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
