import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch

def create_architecture_diagram(output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 폰트 설정 (맑은 고딕 또는 기본 sans-serif)
    plt.rcParams['font.sans-serif'] = ['Malgun Gothic', 'DejaVu Sans', 'Arial']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 캔버스 생성 (16:9 비율, 고해상도 300 DPI)
    fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis('off')

    # 전체 배경색 (Modern Dark Slate)
    fig.patch.set_facecolor('#0b0f19')
    ax.set_facecolor('#0b0f19')

    # 1. 메인 타이틀 영역
    ax.text(8, 8.55, "AWS Web Service Infrastructure Architecture", 
            fontsize=21, fontweight='bold', color='#f8fafc', ha='center', va='center')
    ax.text(8, 8.15, "Project: codyssey_b3-01  |  Region: ap-northeast-2 (Seoul)", 
            fontsize=12, color='#94a3b8', ha='center', va='center')

    # 2. AWS Cloud 영역 (가장 큰 외곽 테두리)
    aws_cloud = FancyBboxPatch((0.5, 0.4), 15.0, 7.35,
                               boxstyle="round,pad=0.3,rounding_size=0.3",
                               ec="#38bdf8", fc="#111827", lw=2.2, linestyle="--", alpha=0.95)
    ax.add_patch(aws_cloud)
    ax.text(0.8, 7.45, "AWS Cloud Region: ap-northeast-2 (Seoul)", 
            fontsize=13, fontweight='bold', color='#38bdf8', va='center')

    # 3. 외부 사용자 (Clients) 영역
    client_box = FancyBboxPatch((0.9, 3.1), 2.3, 3.2,
                                boxstyle="round,pad=0.2,rounding_size=0.2",
                                ec="#64748b", fc="#1e293b", lw=1.8)
    ax.add_patch(client_box)
    
    header_client = FancyBboxPatch((0.9, 5.8), 2.3, 0.5,
                                   boxstyle="round,pad=0.1,rounding_size=0.1",
                                   ec="#64748b", fc="#334155", lw=1)
    ax.add_patch(header_client)
    ax.text(2.05, 6.05, "External Clients", fontsize=11, fontweight='bold', color='#f8fafc', ha='center', va='center')
    
    # 일반 웹 사용자
    u1_box = FancyBboxPatch((1.1, 4.6), 1.9, 1.0,
                            boxstyle="round,pad=0.1,rounding_size=0.1",
                            ec="#0284c7", fc="#0369a1", lw=1)
    ax.add_patch(u1_box)
    ax.text(2.05, 5.25, "Web Visitors", fontsize=10, fontweight='bold', color='#ffffff', ha='center')
    ax.text(2.05, 4.85, "Anywhere (0.0.0.0/0)\nHTTP Port 80", fontsize=8.5, color='#e0f2fe', ha='center')

    # 관리자 (SSH)
    u2_box = FancyBboxPatch((1.1, 3.3), 1.9, 1.0,
                            boxstyle="round,pad=0.1,rounding_size=0.1",
                            ec="#7c3aed", fc="#6d28d9", lw=1)
    ax.add_patch(u2_box)
    ax.text(2.05, 3.95, "Administrator", fontsize=10, fontweight='bold', color='#ffffff', ha='center')
    ax.text(2.05, 3.55, "Admin IP (/32)\nSSH Port 22", fontsize=8.5, color='#f3e8ff', ha='center')

    # 4. VPC 영역 (Virtual Private Cloud)
    vpc_box = FancyBboxPatch((3.7, 0.7), 11.4, 6.75,
                             boxstyle="round,pad=0.25,rounding_size=0.25",
                             ec="#6366f1", fc="#0f172a", lw=2.2)
    ax.add_patch(vpc_box)
    ax.text(4.0, 7.15, "VPC: codyssey-vpc (IPv4 CIDR: 10.0.0.0/16)", 
            fontsize=13, fontweight='bold', color='#818cf8', va='center')

    # 5. Internet Gateway (IGW)
    igw_box = FancyBboxPatch((4.2, 3.3), 1.8, 2.7,
                             boxstyle="round,pad=0.15,rounding_size=0.2",
                             ec="#f59e0b", fc="#1e293b", lw=2)
    ax.add_patch(igw_box)
    
    igw_header = FancyBboxPatch((4.2, 5.5), 1.8, 0.5,
                                boxstyle="round,pad=0.1,rounding_size=0.1",
                                ec="#f59e0b", fc="#b45309", lw=1)
    ax.add_patch(igw_header)
    ax.text(5.1, 5.75, "Internet Gateway", fontsize=9.5, fontweight='bold', color='#ffffff', ha='center', va='center')
    ax.text(5.1, 4.9, "codyssey-igw", fontsize=10.5, fontweight='bold', color='#f8fafc', ha='center')
    ax.text(5.1, 4.1, "State: Attached\nTarget: codyssey-vpc\nBi-directional NAT", fontsize=8.5, color='#cbd5e1', ha='center')

    # 6. Public Route Table 영역
    rt_box = FancyBboxPatch((6.4, 3.3), 2.2, 2.7,
                            boxstyle="round,pad=0.15,rounding_size=0.2",
                            ec="#10b981", fc="#1e293b", lw=1.8)
    ax.add_patch(rt_box)
    
    rt_header = FancyBboxPatch((6.4, 5.5), 2.2, 0.5,
                               boxstyle="round,pad=0.1,rounding_size=0.1",
                               ec="#10b981", fc="#047857", lw=1)
    ax.add_patch(rt_header)
    ax.text(7.5, 5.75, "Public Route Table", fontsize=9.5, fontweight='bold', color='#ffffff', ha='center', va='center')
    ax.text(7.5, 4.95, "codyssey-public-rt", fontsize=10.5, fontweight='bold', color='#f8fafc', ha='center')
    ax.text(7.5, 4.1, "Routes Rules:\n• 0.0.0.0/0 -> codyssey-igw\n• 10.0.0.0/16 -> local", 
            fontsize=8.5, color='#a7f3d0', ha='center')

    # 7. Availability Zone & Public Subnet 영역
    subnet_box = FancyBboxPatch((9.0, 1.0), 5.8, 6.1,
                                boxstyle="round,pad=0.2,rounding_size=0.2",
                                ec="#06b6d4", fc="#131e33", lw=2, linestyle=":")
    ax.add_patch(subnet_box)
    ax.text(9.25, 6.75, "Public Subnet: codyssey-public-subnet-2a", 
            fontsize=12, fontweight='bold', color='#22d3ee', va='center')
    ax.text(9.25, 6.4, "AZ: ap-northeast-2a | CIDR: 10.0.1.0/24 | Auto-assign Public IP: Enabled", 
            fontsize=9, color='#94a3b8', va='center')

    # 8. Security Group 영역
    sg_box = FancyBboxPatch((9.3, 1.3), 5.2, 4.8,
                            boxstyle="round,pad=0.2,rounding_size=0.2",
                            ec="#ec4899", fc="#0f172a", lw=2)
    ax.add_patch(sg_box)
    
    sg_header = FancyBboxPatch((9.3, 5.6), 5.2, 0.5,
                               boxstyle="round,pad=0.1,rounding_size=0.1",
                               ec="#ec4899", fc="#be185d", lw=1)
    ax.add_patch(sg_header)
    ax.text(11.9, 5.85, "Security Group: codyssey-web-sg2 (Virtual Firewall)", 
            fontsize=10.5, fontweight='bold', color='#ffffff', ha='center', va='center')
    ax.text(9.6, 5.3, "Inbound Rules : HTTP (Port 80) -> 0.0.0.0/0  |  SSH (Port 22) -> Admin IP/32\nOutbound Rules: All Traffic -> 0.0.0.0/0", 
            fontsize=8.5, color='#fbcfe8', va='center')

    # 9. EC2 Instance 영역
    ec2_box = FancyBboxPatch((9.6, 1.6), 4.6, 3.4,
                             boxstyle="round,pad=0.2,rounding_size=0.2",
                             ec="#3b82f6", fc="#1e293b", lw=2.2)
    ax.add_patch(ec2_box)
    
    ec2_header = FancyBboxPatch((9.6, 4.55), 4.6, 0.45,
                                boxstyle="round,pad=0.1,rounding_size=0.1",
                                ec="#3b82f6", fc="#1d4ed8", lw=1)
    ax.add_patch(ec2_header)
    ax.text(11.9, 4.78, "EC2 Instance: codyssey-web-server", 
            fontsize=10.5, fontweight='bold', color='#ffffff', ha='center', va='center')
    
    ax.text(11.9, 4.25, "Instance Type: t3.micro  |  OS: Ubuntu Server 24.04 LTS", 
            fontsize=9, color='#93c5fd', ha='center')
    ax.text(11.9, 3.85, "Public IPv4: 3.36.130.0 (External Web)", 
            fontsize=11, fontweight='bold', color='#34d399', ha='center')
    ax.text(11.9, 3.45, "Private IPv4: 10.0.1.153 (Internal Subnet)", 
            fontsize=9.5, color='#cbd5e1', ha='center')
    
    # Nginx Web Server 뱃지
    nginx_box = FancyBboxPatch((10.1, 1.9), 3.6, 1.1,
                               boxstyle="round,pad=0.1,rounding_size=0.1",
                               ec="#10b981", fc="#064e3b", lw=1.5)
    ax.add_patch(nginx_box)
    ax.text(11.9, 2.65, "Nginx Web Server (Active / Running)", 
            fontsize=10.5, fontweight='bold', color='#6ee7b7', ha='center', va='center')
    ax.text(11.9, 2.25, "Listens on Port 80 (HTTP)  |  Health Check: 200 OK", 
            fontsize=8.5, color='#a7f3d0', ha='center', va='center')

    # 10. 트래픽 흐름 화살표 (Traffic Flow Arrows)
    # 10-1. Web Traffic: External -> IGW (하늘색 실선 화살표)
    ax.annotate("", xy=(4.2, 5.1), xytext=(3.2, 5.1),
                arrowprops=dict(arrowstyle="-|>", color="#38bdf8", lw=2.8, mutation_scale=16))
    ax.text(3.7, 5.35, "HTTP :80", fontsize=9, fontweight='bold', color="#38bdf8", ha='center')

    # 10-2. Admin SSH Traffic: External -> IGW (보라색 점선 화살표)
    ax.annotate("", xy=(4.2, 3.8), xytext=(3.2, 3.8),
                arrowprops=dict(arrowstyle="-|>", color="#c084fc", lw=2.2, mutation_scale=16, linestyle="--"))
    ax.text(3.7, 4.05, "SSH :22", fontsize=9, fontweight='bold', color="#c084fc", ha='center')

    # 10-3. IGW -> Route Table
    ax.annotate("", xy=(6.4, 4.65), xytext=(6.0, 4.65),
                arrowprops=dict(arrowstyle="-|>", color="#f59e0b", lw=2.8, mutation_scale=16))

    # 10-4. Route Table -> Subnet / SG
    ax.annotate("", xy=(9.3, 4.65), xytext=(8.6, 4.65),
                arrowprops=dict(arrowstyle="-|>", color="#10b981", lw=2.8, mutation_scale=16))

    # 10-5. SG Inbound -> EC2
    ax.annotate("", xy=(9.6, 3.85), xytext=(9.0, 3.85),
                arrowprops=dict(arrowstyle="-|>", color="#38bdf8", lw=2.8, mutation_scale=16))

    # 11. 범례 (Legend)
    legend_box = FancyBboxPatch((1.0, 0.7), 2.3, 2.0,
                                boxstyle="round,pad=0.1,rounding_size=0.1",
                                ec="#475569", fc="#1e293b", lw=1.2)
    ax.add_patch(legend_box)
    ax.text(2.15, 2.35, "Traffic Legend", fontsize=10, fontweight='bold', color='#f1f5f9', ha='center')
    ax.text(1.2, 1.95, "->  HTTP Traffic (Web)", fontsize=8.5, color='#38bdf8', va='center')
    ax.text(1.2, 1.55, "--> SSH Traffic (Admin)", fontsize=8.5, color='#c084fc', va='center')
    ax.text(1.2, 1.15, "->  AWS Internal Routing", fontsize=8.5, color='#10b981', va='center')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print(f"Architecture diagram successfully generated at {output_path}")

if __name__ == "__main__":
    output_file = r"c:\Users\안재현\Documents\24_code\2609_codyssey\codyssey_b3-01\docs\architecture.png"
    create_architecture_diagram(output_file)
