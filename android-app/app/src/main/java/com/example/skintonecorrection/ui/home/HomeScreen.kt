package com.example.skintonecorrection.ui.home

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.example.skintonecorrection.ui.BrandMark

@Composable
fun HomeScreen(onPickPhoto: () -> Unit) {
    val colors = MaterialTheme.colorScheme
    Scaffold(containerColor = colors.background) { padding ->
        Box(Modifier.fillMaxSize().padding(padding), contentAlignment = Alignment.TopCenter) {
            Column(
                Modifier.widthIn(max = 480.dp).fillMaxWidth().verticalScroll(rememberScrollState())
                    .padding(horizontal = 24.dp, vertical = 22.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    BrandMark()
                    Text("TrueHue", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
                }
                Spacer(Modifier.height(16.dp))
                Text("Correct a portrait", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
                Text("Adjust facial exposure and colour, then compare with the original.",
                    style = MaterialTheme.typography.bodyLarge, color = colors.onSurfaceVariant)
                Surface(
                    onClick = onPickPhoto,
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(24.dp),
                    color = colors.primaryContainer,
                    contentColor = colors.onPrimaryContainer
                ) {
                    Column(
                        Modifier.heightIn(min = 190.dp).padding(24.dp),
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(16.dp, Alignment.CenterVertically)
                    ) {
                        GalleryIcon()
                        Text("Select photo from gallery", style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.SemiBold, textAlign = TextAlign.Center)
                    }
                }
                Text("Your photos stay on this device.", Modifier.align(Alignment.CenterHorizontally),
                    style = MaterialTheme.typography.bodySmall, color = colors.onSurfaceVariant)
            }
        }
    }
}

@Composable
private fun GalleryIcon() {
    val colors = MaterialTheme.colorScheme
    Surface(shape = RoundedCornerShape(18.dp), color = colors.primary, contentColor = colors.onPrimary) {
        val ink = LocalContentColor.current
        Box(Modifier.size(64.dp), contentAlignment = Alignment.Center) {
            Canvas(Modifier.size(30.dp)) {
                val stroke = Stroke(width = 2.dp.toPx(), cap = StrokeCap.Round)
                val edge = stroke.width / 2
                drawRoundRect(ink, Offset(edge, edge), size.copy(width = size.width - stroke.width,
                    height = size.height - stroke.width), CornerRadius(6.dp.toPx()), style = stroke)
                drawCircle(ink, radius = 2.dp.toPx(), center = Offset(size.width * .68f, size.height * .32f))
                val hills = Path().apply {
                    moveTo(size.width * .16f, size.height * .72f)
                    lineTo(size.width * .39f, size.height * .47f)
                    lineTo(size.width * .61f, size.height * .70f)
                    lineTo(size.width * .74f, size.height * .56f)
                    lineTo(size.width * .85f, size.height * .68f)
                }
                drawPath(hills, ink, style = stroke)
            }
        }
    }
}
