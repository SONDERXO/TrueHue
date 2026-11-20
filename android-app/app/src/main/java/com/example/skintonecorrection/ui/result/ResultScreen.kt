package com.example.skintonecorrection.ui.result

import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectHorizontalDragGestures
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.drawWithContent
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.clipRect
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import coil.compose.AsyncImage
import com.example.skintonecorrection.ui.InfoPanel
import com.example.skintonecorrection.ui.PhotoShape
import com.example.skintonecorrection.ui.SharedViewModel
import com.example.skintonecorrection.ui.WorkflowAction
import com.example.skintonecorrection.ui.WorkflowHeader
import com.example.skintonecorrection.ui.WorkflowPage
import com.example.skintonecorrection.ui.photoInfo

@Composable
fun ResultScreen(sharedViewModel: SharedViewModel, onBack: () -> Unit, onReSelect: () -> Unit) {
    val state by sharedViewModel.uiState.collectAsStateWithLifecycle()
    val before = state.photoUsedUri
    val after = state.correctedImageUri
    LaunchedEffect(before, after) { if (before == null || after == null) onBack() }
    if (before == null || after == null) return
    var message by rememberSaveable(after) { mutableStateOf("") }
    var showMask by rememberSaveable(after) { mutableStateOf(false) }
    val info = photoInfo(after)
    val imageExport = rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("image/png")) { destination ->
        if (destination != null) sharedViewModel.export(after, destination) { message = it }
    }
    val reportExport = rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("application/json")) { destination ->
        val source = state.reportUri
        if (destination != null && source != null) sharedViewModel.export(source, destination) { message = it }
    }

    WorkflowPage(actions = {
        WorkflowAction("Save full-size PNG", { imageExport.launch("truehue_correction.png") })
        WorkflowAction("Try another photo", onReSelect, primary = false)
    }) {
        WorkflowHeader("Your results", onBack)
        val unchanged = state.identityControls
        InfoPanel(if (unchanged) "No correction applied" else "Correction complete",
            if (unchanged) "WB314 kept the original appearance." else "Compare with the original before saving.")
        PhotoComparison(before, after, info?.let { it.width.toFloat() / it.height })
        Surface(Modifier.fillMaxWidth(), shape = PhotoShape) {
            Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text("Your export", style = MaterialTheme.typography.titleSmall)
                Text(info?.let { "${it.resolution} · PNG" } ?: "Original size · PNG",
                    style = MaterialTheme.typography.bodyMedium)
            }
        }
        if (message.isNotEmpty()) Text(message, style = MaterialTheme.typography.bodySmall)
        state.maskUri?.let { mask ->
            TextButton(onClick = { showMask = !showMask }) {
                Text(if (showMask) "Hide correction mask" else "Inspect correction mask")
            }
            if (showMask) {
                AsyncImage(mask, "Correction mask. White areas may be corrected.", Modifier.fillMaxWidth().height(220.dp),
                    contentScale = ContentScale.Fit)
            }
        }
        if (state.reportUri != null) TextButton(onClick = { reportExport.launch("truehue_report.json") }) { Text("Save report") }
    }
}

@Composable
private fun PhotoComparison(before: Uri, after: Uri, ratio: Float?) {
    var split by rememberSaveable(before, after) { mutableFloatStateOf(.5f) }
    val previewLimit = (LocalConfiguration.current.screenHeightDp * .28f).coerceIn(144f, 320f).dp
    Surface(Modifier.fillMaxWidth(), shape = PhotoShape) {
        Column(Modifier.padding(12.dp), horizontalAlignment = Alignment.CenterHorizontally) {
            Row(Modifier.fillMaxWidth().padding(bottom = 10.dp), horizontalArrangement = Arrangement.SpaceBetween) {
                Text("Before", style = MaterialTheme.typography.labelLarge)
                Text("After", style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.primary)
            }
            BoxWithConstraints(Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) {
                val aspect = ratio ?: 1f
                val photoWidth = maxWidth
                val height = (photoWidth / aspect).coerceIn(100.dp, previewLimit)
                val scale = if (photoWidth / aspect > previewLimit) ContentScale.Crop else ContentScale.Fit
                Box(Modifier.width(photoWidth).height(height).clip(RoundedCornerShape(12.dp))
                    .background(MaterialTheme.colorScheme.surfaceVariant)
                    .pointerInput(before, after) {
                        detectHorizontalDragGestures(
                            onDragStart = { split = (it.x / size.width).coerceIn(0f, 1f) }
                        ) { change, _ ->
                            split = (change.position.x / size.width).coerceIn(0f, 1f)
                        }
                    }) {
                    AsyncImage(after, "Corrected photo", Modifier.matchParentSize(), contentScale = scale)
                    AsyncImage(before, "Original photo", Modifier.matchParentSize().drawWithContent {
                        clipRect(right = size.width * split) { this@drawWithContent.drawContent() }
                    }, contentScale = scale)
                    Canvas(Modifier.matchParentSize()) {
                        val x = size.width * split
                        drawLine(Color.White, Offset(x, 0f), Offset(x, size.height), strokeWidth = 2.dp.toPx())
                    }
                    Box(Modifier.align(Alignment.CenterStart)
                        .offset(x = (photoWidth * split - 16.dp).coerceIn(0.dp, (photoWidth - 32.dp).coerceAtLeast(0.dp)))
                        .size(32.dp).clip(CircleShape).background(Color.White), contentAlignment = Alignment.Center) {
                        Canvas(Modifier.size(16.dp)) {
                            val stroke = 1.5.dp.toPx()
                            val y = size.height / 2
                            for (side in listOf(-1, 1)) {
                                val tip = Offset(center.x + side * size.width * .30f, y)
                                val inner = center.x + side * size.width * .12f
                                drawLine(Color(0xFF122132), Offset(inner, y - 3.dp.toPx()), tip, stroke, StrokeCap.Round)
                                drawLine(Color(0xFF122132), tip, Offset(inner, y + 3.dp.toPx()), stroke, StrokeCap.Round)
                            }
                        }
                    }
                }
            }
            Slider(value = split, onValueChange = { split = it }, modifier = Modifier.fillMaxWidth()
                .semantics { contentDescription = "Before and after comparison" },
                colors = SliderDefaults.colors(inactiveTrackColor = MaterialTheme.colorScheme.surfaceVariant,
                    inactiveTickColor = Color.Transparent))
            Text("Slide to compare the preview", style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
    }
}
