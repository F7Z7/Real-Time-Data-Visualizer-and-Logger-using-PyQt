

<h1>Real-Time Data Visualizer & Logger ⚡</h1>
<p>A PyQt5-based real-time multi-signal visualizer, math processor, and data logger.</p>

<hr>

<h2>📌 Project Overview</h2>
<p>
This application is a desktop tool built using <strong>PyQt5</strong> and <strong>pyqtgraph</strong>
for real-time acquisition, visualization, and logging of simulated signals.  
It supports modular plotting, live mathematical operations, and flexible CSV/Binary logging.
</p>
<p></p>

<hr>

<h2>✨ Key Features</h2>

<h3>1. Real-Time Multi-Signal Visualization</h3>
<ul>
  <li>Display multiple live graphs simultaneously.</li>
  <li>Each graph uses a dedicated <code>QThread</code> with a <code>DataWorker</code>.</li>
  <li>Global controls for Start All, Stop All, Reset All.</li>
</ul>

<p><em>[images/multi_plots.png]</em></p>

<h3>2. Advanced Signal Math Operations</h3>
<ul>
  <li>Perform A+B, A−B, sin(A), cos(B), sin(A)+2B, etc.</li>
  <li>Math results appear as new live plots.</li>
  <li>NumPy-based vectorized computation.</li>
</ul>

<p><em>[images/math_dialog.jpg]</em></p>
<p><em>[images/math_result.jpg]</em></p>

<h3>3. Robust Data Logging</h3>
<ul>
  <li>Supports <strong>CSV</strong> and <strong>Binary</strong> logging.</li>
  <li>Automatic file rotation based on size limits.</li>
  <li>Optimized logging with minimal disk I/O.</li>
</ul>

<p><em>[images/logged_files.jpg]</em></p>

<h3>4. Interactive Plot Controls</h3>
<ul>
  <li>Zoom, autoscale, and manual axis range settings.</li>
  <li>Right-click context menus for detailed configuration.</li>
  <li>Toggle visibility of individual signals.</li>
</ul>

<p><em>[images/zoom_controls.jpg]</em></p>

<hr>

<h2>🧰 Technology Stack</h2>
<table border="1" cellpadding="6" cellspacing="0">
<tr><th>Library</th><th>Version</th><th>Purpose</th></tr>
<tr><td>PyQt5</td><td>≥ 5.15</td><td>GUI Framework</td></tr>
<tr><td>pyqtgraph</td><td>≥ 0.13</td><td>High-performance plotting</td></tr>
<tr><td>NumPy</td><td>≥ 1.21</td><td>Vectorized computation</td></tr>
</table>

<hr>

<h2>⚙️ Architecture Overview</h2>

<h3>1. Multi-Threading</h3>
<ul>
  <li><code>DataWorker</code> runs in separate threads.</li>
  <li>Generates data at fixed intervals (dt = 0.05s).</li>
  <li>Uses circular buffers (max 500 points).</li>
</ul>

<h3>2. Modular Plot System</h3>
<ul>
  <li><code>Generate_Graph</code> manages plot creation/removal.</li>
  <li><code>GraphWidget</code> handles updates using <code>curve.setData()</code>.</li>
</ul>

<h3>3. Logging Engine</h3>
<ul>
  <li><code>DataLogger</code> manages CSV and binary writes.</li>
  <li>Supports file rotation and size management.</li>
</ul>

<h3>4. Live Math Plotting</h3>
<ul>
  <li>UI-driven expression builder.</li>
  <li>Continuous recomputation using <code>QTimer.singleShot()</code>.</li>
</ul>

<hr>

<h2>📊 Results & Demonstration</h2>

<h3>User Interface</h3>
<p><em>[images/ui_demo.jpg]</em></p>

<h3>Math Operation Example</h3>
<p><em>[images/math_demo.jpg]</em></p>

<h3>Data Logging Output</h3>
<p><em>[images/log_output.jpg]</em></p>

<h3>Zoom & Axis Controls</h3>
<p><em>[images/zoom_demo.jpg]</em></p>

<hr>

<h2>🧪 Testing & Validation</h2>
<ul>
  <li>Tested with up to 6 real-time plots at 20Hz.</li>
  <li>No GUI blocking due to isolated QThreads.</li>
  <li>Circular buffers prevent memory overflow.</li>
  <li>Logging checked for timestamp-value consistency.</li>
</ul>

<p><em>[images/testing.jpg]</em></p>

<hr>

<h2>📂 Suggested Repository Structure</h2>

<pre>
src/
 ├── ui/
 │    ├── main_window.py
 │    ├── dialogs/
 │    └── components/
 ├── data_worker.py
 ├── data_logger.py
 ├── graph_widget.py
 ├── math_functions.py
assets/
 ├── screenshots/
logs/
README.html
</pre>

<hr>

<h2>📜 License</h2>
<p><em>[Add your preferred license here]</em></p>

</body>
</html>
