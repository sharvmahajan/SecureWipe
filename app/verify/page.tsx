"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Textarea } from "@/components/ui/textarea"
import { Shield, FileCheck, Upload, CheckCircle, AlertTriangle, ArrowLeft } from "lucide-react"
import Link from "next/link"
import { ThemeSwitcher } from "@/components/theme-switcher"
import Image from "next/image"

export default function VerificationPage() {
  const [verificationResult, setVerificationResult] = useState<{
    type: "success" | "error" | null
    message: string
  }>({ type: null, message: "" })

  const handleCertificateVerification = async () => {
    // Simulate verification process
    setTimeout(() => {
      setVerificationResult({
        type: "success",
        message: "Certificate is valid and digitally signed. Issued by SecureWipe Enterprise on 2025-01-09.",
      })
    }, 1500)
  }

  const handlePdfVerification = async () => {
    // Simulate PDF verification process
    setTimeout(() => {
      setVerificationResult({
        type: "success",
        message: "PDF signature is valid. Certificate chain verified successfully.",
      })
    }, 2000)
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
              <div>
                <h1 className="text-2xl font-bold text-foreground">SecureWipe</h1>
                <p className="text-sm text-muted-foreground">Public Certificate Verification</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <ThemeSwitcher />
              <Link href="/">
                <Button variant="outline">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Back to Login
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8 max-w-4xl">
        {/* Page Header */}
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-foreground mb-2">Certificate Verification Portal</h2>
          <p className="text-muted-foreground">
            Verify the authenticity and integrity of SecureWipe certificates and PDF documents
          </p>
        </div>

        {/* Verification Results */}
        {verificationResult.type && (
          <Alert
            className={`mb-6 ${verificationResult.type === "success" ? "border-chart-5 bg-chart-5/5" : "border-destructive bg-destructive/5"}`}
          >
            {verificationResult.type === "success" ? (
              <CheckCircle className="h-4 w-4 text-chart-5" />
            ) : (
              <AlertTriangle className="h-4 w-4 text-destructive" />
            )}
            <AlertDescription className={verificationResult.type === "success" ? "text-chart-5" : "text-destructive"}>
              {verificationResult.message}
            </AlertDescription>
          </Alert>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Certificate Verification */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="w-5 h-5 text-primary" />
                Certificate Verification
              </CardTitle>
              <CardDescription>Verify the authenticity of JSON certificates issued by SecureWipe</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="cert-json">Certificate JSON</Label>
                <Textarea
                  id="cert-json"
                  placeholder="Paste the complete certificate JSON here..."
                  className="min-h-[200px] font-mono text-sm"
                />
              </div>

              <Alert>
                <Shield className="h-4 w-4" />
                <AlertDescription>
                  Paste the complete JSON certificate including all metadata and digital signatures.
                </AlertDescription>
              </Alert>

              <Button className="w-full" onClick={handleCertificateVerification}>
                <Shield className="w-4 h-4 mr-2" />
                Verify Certificate
              </Button>
            </CardContent>
          </Card>

          {/* PDF Verification */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileCheck className="w-5 h-5 text-primary" />
                PDF Certificate Verification
              </CardTitle>
              <CardDescription>Verify digitally signed PDF certificates and their integrity</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="pdf-upload">Upload PDF Certificate</Label>
                <div className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary/50 transition-colors cursor-pointer">
                  <Upload className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                  <p className="text-sm text-muted-foreground mb-2">
                    Click to upload or drag and drop your PDF certificate
                  </p>
                  <p className="text-xs text-muted-foreground">Supports PDF files up to 10MB</p>
                </div>
              </div>

              <Alert>
                <FileCheck className="h-4 w-4" />
                <AlertDescription>
                  PDF verification checks digital signatures, certificate chains, and document integrity.
                </AlertDescription>
              </Alert>

              <Button className="w-full" onClick={handlePdfVerification}>
                <FileCheck className="w-4 h-4 mr-2" />
                Verify PDF Signature
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Information Section */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">What We Verify</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-chart-5" />
                <span>Digital signature validity</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-chart-5" />
                <span>Certificate chain integrity</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-chart-5" />
                <span>Timestamp verification</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-chart-5" />
                <span>Document tampering detection</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Compliance Standards</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <div className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-primary" />
                <span>NIST SP 800-88 Rev. 1</span>
              </div>
              <div className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-primary" />
                <span>DoD 5220.22-M</span>
              </div>
              <div className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-primary" />
                <span>ISO/IEC 27040</span>
              </div>
              <div className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-primary" />
                <span>GDPR Article 17</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Security Features</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <div className="flex items-center gap-2">
                <FileCheck className="w-4 h-4 text-chart-5" />
                <span>RSA-4096 encryption</span>
              </div>
              <div className="flex items-center gap-2">
                <FileCheck className="w-4 h-4 text-chart-5" />
                <span>SHA-256 hashing</span>
              </div>
              <div className="flex items-center gap-2">
                <FileCheck className="w-4 h-4 text-chart-5" />
                <span>Blockchain timestamping</span>
              </div>
              <div className="flex items-center gap-2">
                <FileCheck className="w-4 h-4 text-chart-5" />
                <span>Audit trail logging</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
