import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ThemeSwitcher } from "@/components/theme-switcher"
import { Shield, FileCheck, Activity, CheckCircle, Lock, Award, Users, Globe } from "lucide-react"
import Image from "next/image"

export default function InfoPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
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
          <div className="flex items-center gap-4">
            <ThemeSwitcher />
            <Link href="/">
              <Button variant="outline">Login</Button>
            </Link>
            <Link href="/verify">
              <Button variant="outline">Verify Certificate</Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto text-center max-w-4xl">
          <Badge variant="secondary" className="mb-6">
            Enterprise Security Platform
          </Badge>
          <h1 className="text-5xl font-bold text-balance mb-6">
            Professional Data Destruction &<span className="text-primary"> Compliance Certification</span>
          </h1>
          <p className="text-xl text-muted-foreground text-balance mb-8 max-w-2xl mx-auto">
            SecureWipe provides enterprise-grade data destruction services with comprehensive compliance reporting,
            digital certificates, and AI-powered drive health monitoring for complete security assurance.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/register">
              <Button size="lg" className="gap-2">
                <Shield className="h-5 w-5" />
                Get Started
              </Button>
            </Link>
            <Link href="/verify">
              <Button variant="outline" size="lg" className="gap-2 bg-transparent">
                <FileCheck className="h-5 w-5" />
                Verify Certificate
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-16 px-4 bg-muted/30">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Enterprise Security Features</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Comprehensive data destruction platform built for enterprise compliance and security requirements.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <Shield className="h-8 w-8 text-primary mb-2" />
                <CardTitle>Secure Data Wiping</CardTitle>
                <CardDescription>
                  NIST SP 800-88 and DoD 5220.22-M compliant data destruction with multiple overwrite passes
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-primary" />
                    Multiple overwrite algorithms
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-primary" />
                    Compliance verification
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-primary" />
                    Detailed audit logs
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <FileCheck className="h-8 w-8 text-primary mb-2" />
                <CardTitle>Digital Certificates</CardTitle>
                <CardDescription>
                  Cryptographically signed certificates with PDF generation for compliance documentation
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-primary" />
                    Digital signatures
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-primary" />
                    PDF generation
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-primary" />
                    Verification system
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Activity className="h-8 w-8 text-primary mb-2" />
                <CardTitle>AI Drive Health</CardTitle>
                <CardDescription>Machine learning-powered drive health prediction and failure analysis</CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-primary" />
                    Predictive analytics
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-primary" />
                    Health scoring
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-primary" />
                    Risk assessment
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Compliance Section */}
      <section className="py-16 px-4">
        <div className="container mx-auto max-w-4xl text-center">
          <h2 className="text-3xl font-bold mb-8">Industry Compliance Standards</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
            <div className="p-4 border rounded-lg">
              <Award className="h-8 w-8 text-primary mx-auto mb-2" />
              <p className="font-semibold">NIST SP 800-88</p>
            </div>
            <div className="p-4 border rounded-lg">
              <Lock className="h-8 w-8 text-primary mx-auto mb-2" />
              <p className="font-semibold">DoD 5220.22-M</p>
            </div>
            <div className="p-4 border rounded-lg">
              <Users className="h-8 w-8 text-primary mx-auto mb-2" />
              <p className="font-semibold">HIPAA</p>
            </div>
            <div className="p-4 border rounded-lg">
              <Globe className="h-8 w-8 text-primary mx-auto mb-2" />
              <p className="font-semibold">GDPR</p>
            </div>
          </div>
          <p className="text-muted-foreground">
            SecureWipe meets the highest industry standards for data destruction and compliance reporting, ensuring your
            organization maintains regulatory compliance across all jurisdictions.
          </p>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 px-4 bg-primary/5">
        <div className="container mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to Secure Your Data?</h2>
          <p className="text-muted-foreground mb-8">
            Join enterprise organizations worldwide who trust SecureWipe for their data destruction needs.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/register">
              <Button size="lg">Start Free Trial</Button>
            </Link>
            <Link href="/verify">
              <Button variant="outline" size="lg">
                Verify Certificate
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-8 px-4">
        <div className="container mx-auto text-center text-muted-foreground">
          <p>&copy; 2024 SecureWipe. Enterprise Data Destruction Platform.</p>
        </div>
      </footer>
    </div>
  )
}
