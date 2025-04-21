from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt
import numpy as np
import cv2

def generate_shooting_percentage_chart(match, quarter_percentages, output_file):
    quarters = []
    if match:
        for i in range(len(quarter_percentages["team_A"])):
            quarters.append(f"Q{i+1}")
    else:
        for i in range(len(quarter_percentages)):
            quarters.append(f"Q{i+1}")
    
    plt.figure(figsize=(8, 6))
    
    if match:
        team_a_percentages = [round(p * 100, 2) for p in quarter_percentages["team_A"]]
        team_b_percentages = [round(p * 100, 2) for p in quarter_percentages["team_B"]]
        plt.plot(quarters, team_a_percentages, marker='o', linestyle='-', color='b', label='Team A')
        plt.plot(quarters, team_b_percentages, marker='s', linestyle='--', color='r', label='Team B')
        plt.legend(loc="center left", bbox_to_anchor=(1, 0.5), fontsize=15)
    else:
        percentages = [round(p * 100, 2) for p in quarter_percentages]
        plt.plot(quarters, percentages, marker='o', linestyle='-', color='b')
    
    plt.ylim(0, 100)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.xlabel("Quarters", fontsize=18, labelpad=10)
    plt.ylabel("Shooting Percentage (%)", fontsize=18, labelpad=10)
    plt.title("Shooting Percentage Across Quarters", fontsize=20, pad=20) 
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

def generate_shooting_stats_chart(match, quarter_makes, quarter_attempts, chart_file):
    quarters = []
    if match:
        for i in range(len(quarter_makes["team_A"])):
            quarters.append(f"Q{i+1}")
    else:
        for i in range(len(quarter_makes)):
            quarters.append(f"Q{i+1}")
    
    plt.figure(figsize=(9, 6))
    
    if match:
        team_a_makes = quarter_makes["team_A"]
        team_b_makes = quarter_makes["team_B"]

        team_a_attempts = quarter_attempts["team_A"]
        team_b_attempts = quarter_attempts["team_B"]

        plt.plot(quarters, team_a_makes, marker='o', linestyle='-', color='b', label='Team A (Makes)')
        plt.plot(quarters, team_a_attempts, marker='o', linestyle='dotted', color='b', label='Team A (Attempts)')
        plt.plot(quarters, team_b_makes, marker='s', linestyle='-', color='r', label='Team B (Makes)')
        plt.plot(quarters, team_b_attempts, marker='s', linestyle='dotted', color='r', label='Team A (Attempts)')
        plt.legend(loc="center left", bbox_to_anchor=(1, 0.5), fontsize=15)
    else:
        makes = quarter_makes
        attempts = quarter_attempts
        plt.plot(quarters, makes, marker='o', linestyle='-', color='b', label="Makes")
        plt.plot(quarters, attempts, marker='o', linestyle='dotted', color='b', label="Attempts")
        plt.legend(loc="center left", bbox_to_anchor=(1, 0.5), fontsize=15)
    
    if match:
        team_a_data = quarter_makes["team_A"] + quarter_attempts["team_A"]
        team_b_data = quarter_makes["team_B"] + quarter_attempts["team_B"]
        max_y = max(max(team_a_data, default=0), max(team_b_data, default=0))  # Use default=0 for empty lists
    else:
        combined_data = quarter_makes + quarter_attempts
        max_y = max(combined_data, default=0)  # Use default=0 for empty lists
    
    plt.xticks(fontsize=15)
    plt.yticks(range(0, max_y, 1), fontsize=15)  # Increment by 1
    plt.xlabel("Quarters", fontsize=18, labelpad=10)
    plt.ylabel("Shot Made & Attempts", fontsize=18, labelpad=10)
    plt.title("Shot Made & Attempts Across Quarters", fontsize=20, pad=20)
    plt.tight_layout()
    plt.savefig(chart_file)
    plt.close()

def generate_shooting_heatmap(shot_data, output_file, court_image_path, title):
    court_img = cv2.imread(court_image_path)

    # Convert to RGB
    # court_img = cv2.cvtColor(court_img, cv2.COLOR_BGR2RGB)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.imshow(court_img, extent=[-0.5, 300, 280, -0.5])
    # ax.set_aspect('auto')  # Ensure the aspect ratio is correct
    
    made_shots = [shot for shot in shot_data if shot["success"] == True and shot["x"] is not None and shot["y"] is not None]
    miss_shots = [shot for shot in shot_data if shot["success"] == False and shot["x"] is not None and shot["y"] is not None]

    if made_shots:
        ax.scatter([s["x"] for s in made_shots], [s["y"] for s in made_shots], color='green', label='Made', marker="o", s=150)
    if miss_shots:
        ax.scatter([s["x"] for s in miss_shots], [s["y"] for s in miss_shots], color='red', label='Miss', marker="x", s=150)
    
    ax.set_title(f"Shooting Heatmap - {title}", fontsize=20)
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=15)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

def generate_zone_heatmap(shot_data, output_file, court_image_path, title):
    court_img = cv2.imread(court_image_path)

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.imshow(court_img, extent=[-0.5, 300, 280, -0.5])
    
    zone_coordinates = [(45,38),(148,38),(240,38),(148,140),(45,218),(148,218),(240,218),(8,20),(290,20)]

    for i, data in enumerate(shot_data):
        if data == 0 or data == 0.0:
            ax.text(zone_coordinates[i][0], zone_coordinates[i][1], "--", fontsize=20, ha='center', va='center', color='black')
        else:
            ax.text(zone_coordinates[i][0], zone_coordinates[i][1], str(data), fontsize=20, ha='center', va='center', color='black', rotation=90 if i == 7 or i == 8 else 0)

    ax.set_title(title, fontsize=20)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

def generate_basketball_pdf(file_path, court_image_path, **report_data):
    doc = SimpleDocTemplate(file_path, pagesize=landscape(letter), leftMargin=10, rightMargin=10, topMargin=10, bottomMargin=10)
    elements = []
    styles = getSampleStyleSheet()

    # Set alignment to left for all text
    styles['Title'].alignment = 0
    styles['Normal'].alignment = 0
    styles['Heading1'].alignment = 0
    styles['Heading2'].alignment = 0

    match = report_data["is_match"]

    if match == True:
        field_goals_stats = {
            "PAM": [report_data["team_A"]["paint_area_makes"], report_data["team_B"]["paint_area_makes"]],
            "PAT": [report_data["team_A"]["paint_area_attempts"], report_data["team_B"]["paint_area_attempts"]],
            "PAP": [f'{report_data["team_A"]["paint_area_shooting_percentage"]*100:.2f}%', f'{report_data["team_B"]["paint_area_shooting_percentage"]*100:.2f}%'],
            "2PM": [report_data["team_A"]["two_pt_makes"], report_data["team_B"]["two_pt_makes"]],
            "2PT": [report_data["team_A"]["two_pt_attempts"], report_data["team_B"]["two_pt_attempts"]],
            "2PP": [f'{report_data["team_A"]["two_pt_shooting_percentage"]*100:.2f}%', f'{report_data["team_B"]["two_pt_shooting_percentage"]*100:.2f}%'],
            "3PM": [report_data["team_A"]["three_pt_makes"], report_data["team_B"]["three_pt_makes"]],
            "3PT": [report_data["team_A"]["three_pt_attempts"], report_data["team_B"]["three_pt_attempts"]],
            "3PP": [f'{report_data["team_A"]["three_pt_shooting_percentage"]*100:.2f}%', f'{report_data["team_B"]["three_pt_shooting_percentage"]*100:.2f}%'],
            "TOM": [report_data["team_A"]["total_makes"], report_data["team_B"]["total_makes"]],
            "TOT": [report_data["team_A"]["total_attempts"], report_data["team_B"]["total_attempts"]],
            "TOP": [f'{report_data["team_A"]["total_shooting_percentage"]*100:.2f}%', f'{report_data["team_B"]["total_shooting_percentage"]*100:.2f}%'],
        }
    else:    
        field_goals_stats = {
            "PAM": [report_data["paint_area_makes"]],
            "PAT": [report_data["paint_area_attempts"]],
            "PAP": [f'{report_data["paint_area_shooting_percentage"] * 100:.2f}%'],
            "2PM": [report_data["two_pt_makes"]],
            "2PT": [report_data["two_pt_attempts"]],
            "2PP": [f'{report_data["two_pt_shooting_percentage"] * 100:.2f}%'],
            "3PM": [report_data["three_pt_makes"]],
            "3PT": [report_data["three_pt_attempts"]],
            "3PP": [f'{report_data["three_pt_shooting_percentage"] * 100:.2f}%'],
            "TOM": [report_data["total_makes"]],
            "TOT": [report_data["total_attempts"]],
            "TOP": [f'{report_data["total_shooting_percentage"] * 100:.2f}%'],
        }

    # Add Team Statistics
    elements.append(Paragraph("Team Statistics", styles['Title']))

    elements.append(Paragraph("Field Goals Statistics", styles['Heading2']))
    if match == True:
        field_goals_data = [["","Paint Area","","","2-Point","","","3-Point","","","Total", ""],
                            ["", "Made", "Attempted", "Shooting %", "Made", "Attempted", "Shooting %", "Made", "Attempted", "Shooting %", "Made", "Attempted", "Shooting %"],
                            ["Team A"] + [field_goals_stats[key][0] for key in field_goals_stats],
                            ["Team B"] + [field_goals_stats[key][1] for key in field_goals_stats]]
    else:
        field_goals_data = [["","Paint Area","","","2-Point","","","3-Point","","", "Total", ""],
                            ["", "Made", "Attempted", "Shooting %", "Made", "Attempted", "Shooting %", "Made", "Attempted", "Shooting %", "Made", "Attempted", "Shooting %"],
                            ["Team A"] + [field_goals_stats[key][0] for key in field_goals_stats]]
                           
    field_goals_table = Table(field_goals_data, hAlign='LEFT')
    field_goals_table.setStyle(TableStyle([
        ('SPAN', (1, 0), (3, 0)),  # Merge Paint-Area
        ('SPAN', (4, 0), (6, 0)),  # Merge 2-Point
        ('SPAN', (7, 0), (9, 0)),  # Merge 3-Point 
        ('SPAN', (10, 0), (12, 0)),  # Merge 3-Point 
        ('SPAN', (0, 0), (0, 1)), 
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Bold the first row
    ]))
    elements.append(field_goals_table)
    elements.append(Spacer(1, 40))
    
    # Add Shooting Heatmap
    if match == True:
        shot_data_A = report_data["team_A"]["shot_data"]
        shot_data_B = report_data["team_B"]["shot_data"]
        heatmap_file_A = "uploads/shooting_heatmap_a.png"
        heatmap_file_B = "uploads/shooting_heatmap_b.png"
        generate_shooting_heatmap(shot_data_A, heatmap_file_A, court_image_path, "Team A")
        generate_shooting_heatmap(shot_data_B, heatmap_file_B, court_image_path, "Team B")

        heatmap_table = Table(
            [
                [
                    Image(heatmap_file_A, width=300, height=200),  # Team A Heatmap
                    Image(heatmap_file_B, width=300, height=200),  # Team B Heatmap
                ]
            ],
            colWidths=[350],  # Adjust column widths as needed
            hAlign='LEFT'  # Align the table to the left
        )
        heatmap_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align the charts
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertically align the charts
            ('GRID', (0, 0), (-1, -1), 0, colors.white),  # No grid lines
        ]))
        elements.append(Paragraph("Shooting Heatmap", styles['Title']))
        elements.append(heatmap_table)
        elements.append(PageBreak())
    else:
        shot_data = report_data["shot_data"]
        heatmap_file = "uploads/shooting_heatmap_made.png"
        generate_shooting_heatmap(shot_data, heatmap_file, court_image_path, "Team A")
        elements.append(Paragraph("Shooting Heatmap", styles['Title']))
        elements.append(Image(heatmap_file, width=400, height=300))
        elements.append(PageBreak())
    
    # Add Shot Zone Heatmap
    zone_court_image_path = "resources/zone_map.jpg"
    if match == True:
        team_A_zone_makes = report_data["team_A"]["zone_makes"]
        team_A_zone_attempts = report_data["team_A"]["zone_attempts"]
        team_A_zone_pct = [f'{int(value * 100)}%' for value in report_data["team_A"]["zone_shooting_percentage"]]

        team_B_zone_makes = report_data["team_B"]["zone_makes"]
        team_B_zone_attempts = report_data["team_B"]["zone_attempts"]
        team_B_zone_pct = [f'{int(value * 100)}%' for value in report_data["team_B"]["zone_shooting_percentage"]]

        zone_makes_A = "uploads/zone_makes_a.png"
        zone_attempts_A = "uploads/zone_attempts_a.png"
        zone_pct_A = "uploads/zone_pct_a.png"

        zone_makes_B = "uploads/zone_makes_b.png"
        zone_attempts_B = "uploads/zone_attempts_b.png"
        zone_pct_B = "uploads/zone_pct_b.png"

        generate_zone_heatmap(team_A_zone_makes, zone_makes_A, zone_court_image_path, "Shot Zone Makes - Team A")
        generate_zone_heatmap(team_A_zone_attempts, zone_attempts_A, zone_court_image_path, "Shot Zone Attempts - Team A")
        generate_zone_heatmap(team_A_zone_pct, zone_pct_A, zone_court_image_path, "Shot Zone Shooting Percentage - Team A")
        generate_zone_heatmap(team_B_zone_makes, zone_makes_B, zone_court_image_path, "Shot Zone Makes - Team B")
        generate_zone_heatmap(team_B_zone_attempts, zone_attempts_B, zone_court_image_path, "Shot Zone Attempts - Team B")
        generate_zone_heatmap(team_B_zone_pct, zone_pct_B, zone_court_image_path, "Shot Zone Shooting Percentage - Team B")
        
        zone_table_A = Table(
            [
                [
                    Image(zone_makes_A, width=250, height=200),  
                    Image(zone_attempts_A, width=250, height=200), 
                    Image(zone_pct_A, width=250, height=200),
                ]
            ],
            colWidths=[250, 250],  # Adjust column widths as needed
            hAlign='LEFT'  # Align the table to the left
        )
        zone_table_A.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align the charts
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertically align the charts
            ('GRID', (0, 0), (-1, -1), 0, colors.white),  # No grid lines
        ]))

        zone_table_B = Table(
            [
                [
                    Image(zone_makes_B, width=250, height=200),  
                    Image(zone_attempts_B, width=250, height=200), 
                    Image(zone_pct_B, width=250, height=200),
                ]
            ],
            colWidths=[250, 250],  # Adjust column widths as needed
            hAlign='LEFT'  # Align the table to the left
        )
        zone_table_B.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align the charts
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertically align the charts
            ('GRID', (0, 0), (-1, -1), 0, colors.white),  # No grid lines
        ]))

        elements.append(Paragraph("Shot Zone Statistics", styles['Title']))
        elements.append(zone_table_A)
        elements.append(Spacer(1, 20))
        elements.append(zone_table_B)
        elements.append(Spacer(1, 20))
    else:
        zone_makes = report_data["zone_makes"]
        zone_attempts = report_data["zone_attempts"]
        zone_pct = [f'{int(value * 100)}%' for value in report_data["zone_shooting_percentage"]]

        zone_makes_file = "uploads/zone_makes.png"
        zone_attempts_file = "uploads/zone_attempts.png"
        zone_pct_file = "uploads/zone_pct.png"

        generate_zone_heatmap(zone_makes, zone_makes_file, zone_court_image_path, "Shot Zone Makes")
        generate_zone_heatmap(zone_attempts, zone_attempts_file, zone_court_image_path, "Shot Zone Attempts")
        generate_zone_heatmap(zone_pct, zone_pct_file, zone_court_image_path, "Shot Zone Shooting Percentage")

        zone_table = Table(
            [
                [
                    Image(zone_makes_file, width=250, height=200),  
                    Image(zone_attempts_file, width=250, height=200), 
                    Image(zone_pct_file, width=250, height=200),
                ]
            ],
            colWidths=[250, 250],  # Adjust column widths as needed
            hAlign='LEFT'  # Align the table to the left
        )
        zone_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align the charts
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertically align the charts
            ('GRID', (0, 0), (-1, -1), 0, colors.white),  # No grid lines
        ]))
        elements.append(Paragraph("Shot Zone Statistics", styles['Title']))
        elements.append(zone_table)
        elements.append(Spacer(1, 20))
    
    if match == True:
        elements.append(PageBreak())
    
    if match == True:
        quarter_makes = {
            "team_A": report_data["team_A"]["makes"],
            "team_B": report_data["team_B"]["makes"],
        }

        quarter_attempts = {
            "team_A": report_data["team_A"]["attempts"],
            "team_B": report_data["team_B"]["attempts"],
        }

        quarter_percentages = {
            "team_A": report_data["team_A"]["shooting_percentage"],
            "team_B": report_data["team_B"]["shooting_percentage"],
        }
    else:
        quarter_makes = report_data["makes"]
        quarter_attempts = report_data["attempts"]
        quarter_percentages = report_data["shooting_percentage"]

    # Add Shooting Percentage Chart
    if quarter_percentages and quarter_attempts and quarter_makes:
        percentage_chart_file = "uploads/shooting_percentage_chart.png"
        stats_chart_file = "uploads/shooting_stats_chart.png"

        generate_shooting_percentage_chart(match, quarter_percentages, percentage_chart_file)
        generate_shooting_stats_chart(match, quarter_makes, quarter_attempts, stats_chart_file)

        # Create a table with two columns to place the charts side by side
        chart_table = Table(
            [
                [
                    Image(percentage_chart_file, width=300, height=200),  # Shooting Percentage Chart
                    Image(stats_chart_file, width=300, height=200),       # Shooting Stats Chart
                ]
            ],
            colWidths=[400],
            hAlign='LEFT'  # Align the table to the left
        )
        chart_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align the charts
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertically align the charts
            ('GRID', (0, 0), (-1, -1), 0, colors.white),  # No grid lines
        ]))

        elements.append(Paragraph("Shots Trend Across Quarters", styles['Title']))
        elements.append(chart_table)
        elements.append(Spacer(1, 12))

    doc.build(elements)
    print(f"PDF generated successfully: {file_path}")

