"use client"

import type React from "react"
import Image from "next/image"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { ThemeSwitcher } from "@/components/theme-switcher"
import { Lock, User } from "lucide-react"
import Link from "next/link"

export default function LoginPage() {
  const [credentials, setCredentials] = useState({ username: "", password: "" })
  const [isLoading, setIsLoading] = useState(false)

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    // Simulate login process
    setTimeout(() => {
      setIsLoading(false)
      // Redirect to dashboard
      window.location.href = "/dashboard"
    }, 1500)
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6">
      <div className="absolute top-4 right-4">
        <ThemeSwitcher />
      </div>

      <div className="w-full max-w-md space-y-6">
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="flex items-center justify-center mx-auto">
            <Image
              src="/images/securewipe-logo.png"
              alt="SecureWipe Logo"
              width={300}
              height={90}
              className="h-24 w-auto"
            />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-foreground">SecureWipe</h1>
            <p className="text-muted-foreground">Enterprise Data Destruction Platform</p>
          </div>
        </div>

        {/* Login Form */}
        <Card>
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl text-center">Sign In</CardTitle>
            <CardDescription className="text-center">Enter your credentials to access the platform</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleLogin} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="username">Username</Label>
                <div className="relative">
                  <User className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="username"
                    type="text"
                    placeholder="Enter your username"
                    className="pl-10"
                    value={credentials.username}
                    onChange={(e) => setCredentials({ ...credentials, username: e.target.value })}
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="password"
                    type="password"
                    placeholder="Enter your password"
                    className="pl-10"
                    value={credentials.password}
                    onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
                    required
                  />
                </div>
              </div>

              <Button type="submit" className="w-full" size="lg" disabled={isLoading}>
                {isLoading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin mr-2" />
                    Signing In...
                  </>
                ) : (
                  <>
                    <Lock className="w-4 h-4 mr-2" />
                    Sign In
                  </>
                )}
              </Button>
            </form>

            <div className="mt-6 pt-6 border-t border-border">
              <Alert>
                <Lock className="h-4 w-4" />
                <AlertDescription>
                  Access to this system is restricted to authorized personnel only. All activities are logged and
                  monitored.
                </AlertDescription>
              </Alert>
            </div>
          </CardContent>
        </Card>

        {/* Registration Link */}
        <div className="text-center">
          <p className="text-sm text-muted-foreground mb-2">Don't have an account?</p>
          <Link href="/register">
            <Button variant="outline" size="sm">
              Create Account
            </Button>
          </Link>
        </div>

        {/* Platform Information Link */}
        <div className="text-center">
          <p className="text-sm text-muted-foreground mb-2">Learn more about SecureWipe</p>
          <Link href="/info">
            <Button variant="outline" size="sm">
              Platform Information
            </Button>
          </Link>
        </div>

        {/* Public Access */}
        <div className="text-center">
          <p className="text-sm text-muted-foreground mb-2">Need to verify a certificate?</p>
          <Link href="/verify">
            <Button variant="outline" size="sm">
              Public Verification Portal
            </Button>
          </Link>
        </div>

        {/* Compliance Badges */}
        <div className="flex justify-center space-x-4">
          <div className="text-center">
            <div className="text-xs text-muted-foreground">NIST SP 800-88</div>
            <div className="text-xs font-medium text-chart-5">Compliant</div>
          </div>
          <div className="text-center">
            <div className="text-xs text-muted-foreground">DoD 5220.22-M</div>
            <div className="text-xs font-medium text-primary">Certified</div>
          </div>
        </div>
      </div>
    </div>
  )
}
