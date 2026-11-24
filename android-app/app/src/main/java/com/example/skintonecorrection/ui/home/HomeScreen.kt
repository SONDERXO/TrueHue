package com.example.skintonecorrection.ui.home

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.semantics.LiveRegionMode
import androidx.compose.ui.semantics.liveRegion
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.skintonecorrection.ui.BrandMark
import com.example.skintonecorrection.ui.InfoPanel
import com.example.skintonecorrection.ui.WorkflowAction

@Composable
fun HomeScreen(onPickPhoto: () -> Unit, onTakePhoto: () -> Unit, cameraMessage: String?) {
    val colors = MaterialTheme.colorScheme
    Scaffold(containerColor = colors.background) { insets ->
        Box(Modifier.fillMaxSize().padding(insets), contentAlignment = Alignment.Center) {
            Column(
                Modifier.widthIn(max = 400.dp).fillMaxWidth().verticalScroll(rememberScrollState())
                    .padding(horizontal = 18.dp, vertical = 16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                HomeIntro()
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    WorkflowAction("Choose photo", onPickPhoto)
                    WorkflowAction("Take a photo", onTakePhoto, primary = false)
                }
                if (cameraMessage != null) {
                    Text(cameraMessage, Modifier.semantics { liveRegion = LiveRegionMode.Polite },
                        style = MaterialTheme.typography.bodyMedium, color = colors.error)
                }
                InfoPanel("For best results", "Face the camera in even light and keep your face in view.")
                Text("Your photos stay on this device.", style = MaterialTheme.typography.bodySmall,
                    color = colors.onSurfaceVariant, modifier = Modifier.align(Alignment.CenterHorizontally))
            }
        }
    }
}

@Composable
private fun HomeIntro() {
    Box(
        Modifier.fillMaxWidth().clip(RoundedCornerShape(22.dp))
            .background(Brush.linearGradient(listOf(Color(0xFF073D39), Color(0xFF086D60))))
    ) {
        Canvas(Modifier.matchParentSize()) {
            val centre = Offset(size.width * .94f, size.height * .24f)
            for (radius in listOf(40.dp, 66.dp, 94.dp)) {
                drawCircle(Color.White.copy(alpha = .12f), radius.toPx(), centre, style = Stroke(1.dp.toPx()))
            }
        }
        Column(Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                BrandMark(40.dp)
                Text("TrueHue", style = MaterialTheme.typography.titleMedium,
                    color = Color.White, fontWeight = FontWeight.Bold)
            }
            Text("Portrait lighting and colour", style = MaterialTheme.typography.titleLarge,
                color = Color.White, fontWeight = FontWeight.Bold, letterSpacing = (-.3).sp)
            Text("Adjust a portrait, compare it with the original, and save at full resolution.",
                style = MaterialTheme.typography.bodyMedium, color = Color(0xFFE0F5EF))
        }
    }
}
