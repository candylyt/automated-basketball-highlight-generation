from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt
import numpy as np
import cv2

def generate_shooting_percentage_chart(quarter_percentages, output_file, match=True):
    quarters = list(quarter_percentages.keys())
    
    plt.figure(figsize=(6, 4))
    
    if match:
        team_a_percentages = [quarter_percentages[q][0] for q in quarters]
        team_b_percentages = [quarter_percentages[q][1] for q in quarters]
        plt.plot(quarters, team_a_percentages, marker='o', linestyle='-', color='b', label='Team A')
        plt.plot(quarters, team_b_percentages, marker='s', linestyle='--', color='r', label='Team B')
        plt.legend()
    else:
        percentages = list(quarter_percentages.values())
        plt.plot(quarters, percentages, marker='o', linestyle='-', color='b')
    
    plt.xlabel("Quarters")
    plt.ylabel("Shooting Percentage")
    plt.title("Shooting Percentage Across Quarters")
    plt.grid(True)
    plt.savefig(output_file)
    plt.close()

def generate_shooting_heatmap(shot_data, output_file, court_image_path):
    court_img = cv2.imread(court_image_path)
    court_img = cv2.cvtColor(court_img, cv2.COLOR_BGR2RGB)
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.imshow(court_img, extent=[0, 15, 0, 28])
    
    team_a_shots = [shot for shot in shot_data if shot[2] == "A"]
    team_b_shots = [shot for shot in shot_data if shot[2] == "B"]
    
    if team_a_shots:
        ax.scatter([s[0] for s in team_a_shots], [s[1] for s in team_a_shots], color='blue', label='Team A', alpha=0.7)
    if team_b_shots:
        ax.scatter([s[0] for s in team_b_shots], [s[1] for s in team_b_shots], color='red', label='Team B', alpha=0.7)
    
    ax.set_title("Shooting Heatmap (Made Shots)")
    ax.legend()
    plt.savefig(output_file)
    plt.close()

def generate_basketball_pdf(file_path, game_summary, field_goals_stats, shot_types_stats, shot_zones_stats, match=True, quarter_scores=None, quarter_percentages=None, shot_data=None, court_image_path=None):
    doc = SimpleDocTemplate(file_path, leftMargin=50, rightMargin=50, topMargin=50, bottomMargin=50)
    elements = []
    styles = getSampleStyleSheet()

    # Set alignment to left for all text
    styles['Title'].alignment = 0
    styles['Normal'].alignment = 0
    styles['Heading1'].alignment = 0
    styles['Heading2'].alignment = 0

    # Add Game Summary
    elements.append(Paragraph("Game Summary", styles['Title']))
    for key, value in game_summary.items():
        elements.append(Paragraph(f"{key}: {value}", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Add Quarter Scores if available
    if match and quarter_scores:
        elements.append(Paragraph("Quarter Scores", styles['Title']))
        transposed_quarter_data = [["", "Q1", "Q2", "Q3", "Q4"],
                                   ["Team A"] + [quarter_scores[q][0] for q in quarter_scores],
                                   ["Team B"] + [quarter_scores[q][1] for q in quarter_scores]]
        table = Table(transposed_quarter_data, colWidths=[80] * 5, hAlign='LEFT')
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))
    
    # Add Team Statistics
    elements.append(Paragraph("Team Statistics", styles['Title']))

    elements.append(Paragraph("Field Goals Statistics", styles['Heading2']))
    field_goals_data = [["","Field Goals","","","Free Throws","","","3-Point","",""],
                         ["", "FGM", "FGA", "FG%", "FTM", "FTA", "FT%", "3PM", "3PA", "3P%","eFG%","TS%"],
                         ["Team A"] + [field_goals_stats[key][0] for key in field_goals_stats],
                         ["Team B"] + [field_goals_stats[key][1] for key in field_goals_stats]]
    field_goals_table = Table(field_goals_data, hAlign='LEFT')
    field_goals_table.setStyle(TableStyle([
        ('SPAN', (1, 0), (3, 0)),  # Merge Field Goals across FGM, FGA, FG%
        ('SPAN', (4, 0), (6, 0)),  # Merge Free Throws across FTM, FTA, FT%
        ('SPAN', (7, 0), (9, 0)),  # Merge 3-Point across 3PM, 3PA, 3P%
        ('SPAN', (0, 0), (0, 1)), 
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    elements.append(field_goals_table)
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Shot Types Statistics", styles['Heading2']))
    shot_types_data = [["", "Contested Shots", "", "", "Uncontested Shots", "", "", "Total Shots"],
                        ["", "Made", "Attempted", "Shooting %", "Made", "Attempted", "Shooting %", "Made", "Attempted", "Shooting %"],
                        ["Team A"] + [shot_types_stats[key][0] for key in shot_types_stats],
                        ["Team B"] + [shot_types_stats[key][1] for key in shot_types_stats]]
    shot_types_table = Table(shot_types_data, hAlign='LEFT')
    shot_types_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('SPAN', (1, 0), (3, 0)),
        ('SPAN', (4, 0), (6, 0)),
        ('SPAN', (7, 0), (9, 0)),
        ('SPAN', (0, 0), (0, 1))
    ]))
    elements.append(shot_types_table)
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Shot Zone Statistics", styles['Heading2']))
    shooting_zones_data = [["", "Paint Area", "", "", "Mid-Range", "", "", "3-Point"],
                        ["", "Made", "Attempted", "Shooting %", "Made", "Attempted", "Shooting %", "Made", "Attempted", "Shooting %"],
                        ["Team A"] + [shot_zones_stats[key][0] for key in shot_zones_stats],
                        ["Team B"] + [shot_zones_stats[key][1] for key in shot_zones_stats]]
    shooting_zones_table = Table(shooting_zones_data, hAlign='LEFT')
    shooting_zones_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('SPAN', (1, 0), (3, 0)),
        ('SPAN', (4, 0), (6, 0)),
        ('SPAN', (7, 0), (9, 0)),
        ('SPAN', (0, 0), (0, 1))
    ]))
    elements.append(shooting_zones_table)
    elements.append(Spacer(1, 12))
    
    # Insert a Page Break before Shooting Percentage Chart
    elements.append(PageBreak())

    # Add Shooting Percentage Chart
    if quarter_percentages:
        chart_file = "uploads/shooting_percentage_chart.png"
        generate_shooting_percentage_chart(quarter_percentages, chart_file)
        elements.append(Paragraph("Shots Trend Across Quarters", styles['Title']))
        elements.append(Image(chart_file, width=400, height=300))
        elements.append(Spacer(1, 12))
    
    # Add Shooting Heatmap
    if shot_data:
        heatmap_file = "uploads/shooting_heatmap.png"
        generate_shooting_heatmap(shot_data, heatmap_file, court_image_path)
        elements.append(Paragraph("Shooting Heatmap", styles['Title']))
        elements.append(Image(heatmap_file, width=400, height=300))
        elements.append(Spacer(1, 12))
    
    doc.build(elements)
    print(f"PDF generated successfully: {file_path}")

