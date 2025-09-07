"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ThemeSwitcher } from "@/components/theme-switcher"
import Image from "next/image"
import {
  Shield,
  HardDrive,
  FileCheck,
  Activity,
  Download,
  CheckCircle,
  AlertTriangle,
  Zap,
  LogOut,
  User,
} from "lucide-react"

export default function SecureWipeDashboard() {
  const [activeWipes, setActiveWipes] = useState([
    { id: "wipe-001", device: "Samsung SSD 970", progress: 75, status: "wiping" },
    { id: "wipe-002", device: "WD Black 2TB", progress: 100, status: "completed" },
  ])

  const [certificates, setCertificates] = useState([
    { id: "cert-001", device: "Samsung SSD 970", date: "2025-01-09", status: "signed" },
    { id: "cert-002", device: "WD Black 2TB", date: "2025-01-08", status: "pending" },
  ])

  const handleLogout = () => {
    // Redirect to login page
    window.location.href = "/"
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center">
                <Image
                  src="/images/securewipe-logo.png"
                  alt="SecureWipe Logo"
                  width={300}
                  height={90}
                  className="h-24 w-auto"
                />
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Badge variant="outline" className="bg-chart-5/10 text-chart-5 border-chart-5/20">
                NIST SP 800-88 Compliant
              </Badge>
              <Badge variant="outline" className="bg-primary/10 text-primary border-primary/20">
                DoD 5220.22-M Certified
              </Badge>
              <ThemeSwitcher />
              <div className="flex items-center space-x-2">
                <div className="flex items-center space-x-2 px-3 py-2 bg-muted rounded-lg">
                  <User className="w-4 h-4 text-muted-foreground" />
                  <span className="text-sm font-medium">Admin User</span>
                </div>
                <Button variant="outline" size="sm" onClick={handleLogout}>
                  <LogOut className="w-4 h-4 mr-2" />
                  Logout
                </Button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8">
        {/* Dashboard Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Wipes</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">2</div>
              <p className="text-xs text-muted-foreground">1 in progress</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Certificates Issued</CardTitle>
              <FileCheck className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-chart-5">147</div>
              <p className="text-xs text-muted-foreground">+12 this month</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Drive Health</CardTitle>
              <HardDrive className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-chart-5">85%</div>
              <p className="text-xs text-muted-foreground">Excellent condition</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Compliance Score</CardTitle>
              <Shield className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">100%</div>
              <p className="text-xs text-muted-foreground">Fully compliant</p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Tabs */}
        <Tabs defaultValue="wipe" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="wipe" className="flex items-center gap-2">
              <Zap className="w-4 h-4" />
              Data Wipe
            </TabsTrigger>
            <TabsTrigger value="health" className="flex items-center gap-2">
              <Activity className="w-4 h-4" />
              Drive Health
            </TabsTrigger>
            <TabsTrigger value="certificates" className="flex items-center gap-2">
              <FileCheck className="w-4 h-4" />
              Certificates
            </TabsTrigger>
          </TabsList>

          {/* Data Wipe Tab */}
          <TabsContent value="wipe" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Start New Wipe */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Zap className="w-5 h-5 text-primary" />
                    Start New Wipe Operation
                  </CardTitle>
                  <CardDescription>
                    Configure and initiate secure data destruction with compliance standards
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="device-id">Device Serial Number</Label>
                      <Input id="device-id" placeholder="e.g., S4XNNE0M123456" />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="device-model">Device Model</Label>
                      <Input id="device-model" placeholder="e.g., Samsung SSD 970 EVO" />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="firmware">Firmware Version</Label>
                      <Input id="firmware" placeholder="e.g., 2B2QEXM7" />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="capacity">Capacity (GB)</Label>
                      <Input id="capacity" type="number" placeholder="e.g., 1000" />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="dev-path">Device Path</Label>
                    <Input id="dev-path" placeholder="/path/to/device or folder" />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="user-id">User ID</Label>
                      <Input id="user-id" placeholder="admin001" />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="username">Username</Label>
                      <Input id="username" placeholder="John Doe" />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="wipe-method">Wiping Method</Label>
                    <Select defaultValue="zero-fill-1pass">
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="zero-fill-1pass">Zero Fill (1 Pass) - NIST SP 800-88</SelectItem>
                        <SelectItem value="dod-3pass">DoD 5220.22-M (3 Pass)</SelectItem>
                        <SelectItem value="random-7pass">Random Data (7 Pass)</SelectItem>
                        <SelectItem value="gutmann-35pass">Gutmann Method (35 Pass)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <Alert>
                    <Shield className="h-4 w-4" />
                    <AlertDescription>
                      This operation will permanently destroy all data on the selected device. Ensure you have proper
                      authorization before proceeding.
                    </AlertDescription>
                  </Alert>

                  <Button className="w-full" size="lg">
                    <Zap className="w-4 h-4 mr-2" />
                    Start Secure Wipe
                  </Button>
                </CardContent>
              </Card>

              {/* Active Wipe Operations */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="w-5 h-5 text-primary" />
                    Active Wipe Operations
                  </CardTitle>
                  <CardDescription>Monitor ongoing data destruction processes</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {activeWipes.map((wipe) => (
                    <div key={wipe.id} className="p-4 border border-border rounded-lg space-y-3">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium">{wipe.device}</p>
                          <p className="text-sm text-muted-foreground">ID: {wipe.id}</p>
                        </div>
                        <Badge
                          variant={wipe.status === "completed" ? "default" : "secondary"}
                          className={wipe.status === "completed" ? "bg-chart-5 text-white" : ""}
                        >
                          {wipe.status === "completed" ? (
                            <CheckCircle className="w-3 h-3 mr-1" />
                          ) : (
                            <Activity className="w-3 h-3 mr-1" />
                          )}
                          {wipe.status}
                        </Badge>
                      </div>

                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Progress</span>
                          <span>{wipe.progress}%</span>
                        </div>
                        <Progress value={wipe.progress} className="h-2" />
                      </div>

                      {wipe.status === "completed" && (
                        <Button variant="outline" size="sm" className="w-full bg-transparent">
                          <Download className="w-4 h-4 mr-2" />
                          Download Certificate
                        </Button>
                      )}
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Drive Health Tab */}
          <TabsContent value="health" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Health Check */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="w-5 h-5 text-primary" />
                    Drive Health Analysis
                  </CardTitle>
                  <CardDescription>AI-powered drive health prediction using SMART data</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="drive-id">Drive ID for Analysis</Label>
                    <Input id="drive-id" placeholder="Enter drive ID (e.g., 555 for test data)" />
                  </div>

                  <Button className="w-full">
                    <Activity className="w-4 h-4 mr-2" />
                    Analyze Drive Health
                  </Button>

                  <Alert>
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>
                      Health analysis uses machine learning models trained on SMART attributes and failure patterns.
                    </AlertDescription>
                  </Alert>
                </CardContent>
              </Card>

              {/* Health Results */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <HardDrive className="w-5 h-5 text-primary" />
                    Health Status
                  </CardTitle>
                  <CardDescription>Current drive health assessment</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="text-center space-y-2">
                    <div className="text-4xl font-bold text-chart-5">85%</div>
                    <p className="text-muted-foreground">Health Score</p>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Overall Health</span>
                      <span className="text-chart-5 font-medium">Excellent</span>
                    </div>
                    <Progress value={85} className="h-2" />
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="space-y-1">
                      <p className="text-muted-foreground">Temperature</p>
                      <p className="font-medium">42°C</p>
                    </div>
                    <div className="space-y-1">
                      <p className="text-muted-foreground">Power Cycles</p>
                      <p className="font-medium">1,247</p>
                    </div>
                    <div className="space-y-1">
                      <p className="text-muted-foreground">Reallocated Sectors</p>
                      <p className="font-medium text-chart-5">0</p>
                    </div>
                    <div className="space-y-1">
                      <p className="text-muted-foreground">Pending Sectors</p>
                      <p className="font-medium text-chart-5">0</p>
                    </div>
                  </div>

                  <Alert>
                    <CheckCircle className="h-4 w-4" />
                    <AlertDescription>
                      Drive is operating within normal parameters. No immediate replacement needed.
                    </AlertDescription>
                  </Alert>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Certificates Tab */}
          <TabsContent value="certificates" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileCheck className="w-5 h-5 text-primary" />
                  Certificate Management
                </CardTitle>
                <CardDescription>View, download, and manage wipe certificates</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {certificates.map((cert) => (
                    <div
                      key={cert.id}
                      className="flex items-center justify-between p-4 border border-border rounded-lg"
                    >
                      <div className="space-y-1">
                        <p className="font-medium">{cert.device}</p>
                        <p className="text-sm text-muted-foreground">
                          Certificate ID: {cert.id} • Issued: {cert.date}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge
                          variant={cert.status === "signed" ? "default" : "secondary"}
                          className={cert.status === "signed" ? "bg-chart-5 text-white" : ""}
                        >
                          {cert.status === "signed" ? (
                            <CheckCircle className="w-3 h-3 mr-1" />
                          ) : (
                            <AlertTriangle className="w-3 h-3 mr-1" />
                          )}
                          {cert.status}
                        </Badge>
                        <Button variant="outline" size="sm">
                          <Download className="w-4 h-4 mr-2" />
                          Download PDF
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
