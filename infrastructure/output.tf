output "xc3_url" {
  description = "DNS of the XC3 Dashboard"
  value       = module.xc3.load_balancer_dns
 }
