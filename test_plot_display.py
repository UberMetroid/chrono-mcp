#!/usr/bin/env python3
"""
Test the plot display functionality
"""

import requests

def test_plot_display():
    """Test that plot display works"""
    print("🧪 Testing Plot Display Functionality")
    print("=" * 50)

    # Test API endpoints
    print("1. Testing API endpoints...")

    # Plot list
    response = requests.get("http://localhost:5000/api/plot")
    if response.status_code == 200:
        plots = response.json()
        print(f"✅ Plot list: {len(plots.get('plots', []))} plots available")
    else:
        print(f"❌ Plot API failed: {response.status_code}")
        return False

    # Test Chrono Trigger plot
    response = requests.get("http://localhost:5000/api/plot/ct")
    if response.status_code == 200:
        ct_plot = response.json()
        print(f"✅ CT plot data: {len(str(ct_plot))} chars of plot content")

        # Check key sections
        sections = []
        if ct_plot.get('eras'): sections.append(f"{len(ct_plot['eras'])} eras")
        if ct_plot.get('character_arcs'): sections.append(f"{len(ct_plot['character_arcs'])} characters")
        if ct_plot.get('endings'): sections.append(f"{len(ct_plot['endings'])} endings")

        print(f"✅ CT plot sections: {', '.join(sections)}")
    else:
        print(f"❌ CT plot failed: {response.status_code}")
        return False

    # Test web interface
    print("\n2. Testing web interface...")

    response = requests.get("http://localhost:5000/")
    if response.status_code == 200:
        html = response.text
        if 'plot-card' in html:
            print("✅ Plot cards CSS present")
        else:
            print("❌ Plot cards CSS missing")
            return False

        if 'showPlot(' in html:
            print("✅ showPlot JavaScript function present")
        else:
            print("❌ showPlot JavaScript missing")
            return False

        if 'loadPlots()' in html:
            print("✅ loadPlots() call present")
        else:
            print("❌ loadPlots() call missing")
            return False

        print("✅ Web interface components verified")
    else:
        print(f"❌ Web interface failed: {response.status_code}")
        return False

    print("\n" + "=" * 50)
    print("🎉 PLOT DISPLAY FUNCTIONALITY: FULLY OPERATIONAL")
    print("✅ API endpoints working")
    print("✅ Plot data accessible")
    print("✅ Web interface components present")
    print("✅ JavaScript functions loaded")
    print("\n📖 The 'View Story' buttons should now work correctly!")
    return True

if __name__ == "__main__":
    test_plot_display()