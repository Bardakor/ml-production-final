'use client'

import { useState, useEffect, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Activity, Brain, TrendingUp, AlertCircle } from 'lucide-react'
import axios from 'axios'

interface HealthData {
  status: string;
  model_loaded: boolean;
  timestamp: string;
}

interface ModelInfo {
  model_loaded: boolean;
  model_version: string;
  model_type: string;
  timestamp: string;
}

interface PredictionResponse {
  prediction: number;
  confidence: number;
  model_version: string;
  timestamp: string;
}

export default function Home() {
  const [features, setFeatures] = useState(['', '', '', ''])
  const [prediction, setPrediction] = useState<number | null>(null)
  const [confidence, setConfidence] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)
  const [health, setHealth] = useState<HealthData | null>(null)
  const [modelInfo, setModelInfo] = useState<ModelInfo | null>(null)

  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

  const fetchHealth = useCallback(async () => {
    try {
      const response = await axios.get<HealthData>(`${backendUrl}/`)
      setHealth(response.data)
    } catch (error: unknown) {
      console.error('Health check failed:', error)
    }
  }, [backendUrl])

  const fetchModelInfo = useCallback(async () => {
    try {
      const response = await axios.get<ModelInfo>(`${backendUrl}/model/info`)
      setModelInfo(response.data)
    } catch (error: unknown) {
      console.error('Model info fetch failed:', error)
    }
  }, [backendUrl])

  useEffect(() => {
    fetchHealth()
    fetchModelInfo()
  }, [fetchHealth, fetchModelInfo])

  const handlePredict = async () => {
    if (features.some(f => f === '')) {
      alert('Please fill in all feature values')
      return
    }

    setLoading(true)
    try {
      const response = await axios.post<PredictionResponse>(`${backendUrl}/predict`, {
        features: features.map(f => parseFloat(f)),
        user_id: 'demo-user'
      })

      setPrediction(response.data.prediction)
      setConfidence(response.data.confidence)
    } catch (error: unknown) {
      console.error('Prediction failed:', error)
      alert('Prediction failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleFeatureChange = (index: number, value: string) => {
    const newFeatures = [...features]
    newFeatures[index] = value
    setFeatures(newFeatures)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold text-gray-900">ML Production App</h1>
          <p className="text-lg text-gray-600">Real-time machine learning predictions</p>
        </div>

        {/* Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">System Status</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {health?.status === 'healthy' ? (
                  <span className="text-green-600">Healthy</span>
                ) : (
                  <span className="text-red-600">Offline</span>
                )}
              </div>
              <p className="text-xs text-muted-foreground">
                Last checked: {health?.timestamp ? new Date(health.timestamp).toLocaleTimeString() : 'Never'}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Model Status</CardTitle>
              <Brain className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {modelInfo?.model_loaded ? (
                  <span className="text-green-600">Loaded</span>
                ) : (
                  <span className="text-red-600">Not Loaded</span>
                )}
              </div>
              <p className="text-xs text-muted-foreground">
                Version: {modelInfo?.model_version || 'Unknown'}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Model Type</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {modelInfo?.model_type || 'Unknown'}
              </div>
              <p className="text-xs text-muted-foreground">
                Ready for predictions
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Prediction Form */}
        <Card>
          <CardHeader>
            <CardTitle>Make a Prediction</CardTitle>
            <CardDescription>
              Enter 4 feature values to get a machine learning prediction
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {features.map((feature, index) => (
                <div key={index} className="space-y-2">
                  <Label htmlFor={`feature-${index}`}>Feature {index + 1}</Label>
                  <Input
                    id={`feature-${index}`}
                    type="number"
                    step="any"
                    placeholder={`Enter value for feature ${index + 1}`}
                    value={feature}
                    onChange={(e) => handleFeatureChange(index, e.target.value)}
                  />
                </div>
              ))}
            </div>

            <Button 
              onClick={handlePredict} 
              disabled={loading || !health?.status}
              className="w-full"
            >
              {loading ? 'Predicting...' : 'Get Prediction'}
            </Button>

            {prediction !== null && (
              <Card className="bg-green-50 border-green-200">
                <CardContent className="pt-6">
                  <div className="text-center space-y-2">
                    <div className="text-3xl font-bold text-green-700">
                      {prediction.toFixed(4)}
                    </div>
                    <div className="text-sm text-green-600">
                      Confidence: {confidence ? (confidence * 100).toFixed(1) : 0}%
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {!health?.status && (
              <Card className="bg-red-50 border-red-200">
                <CardContent className="pt-6">
                  <div className="flex items-center space-x-2 text-red-700">
                    <AlertCircle className="h-5 w-5" />
                    <span>Backend service is not available</span>
                  </div>
                </CardContent>
              </Card>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
