package com.example.skintonecorrection.ui.result

import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectHorizontalDragGestures
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
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
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import coil.compose.AsyncImage
import com.example.skintonecorrection.R
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
    val imageExport = rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("image/png")) { destination ->
        if (destination != null) sharedViewModel.export(after, destination) { message = it }
    }
    WorkflowPage(actions = {
        if (!state.identityControls) {
            WorkflowAction("Save photo", { imageExport.launch("truehue_correction.png") })
        }
        WorkflowAction("Try another photo", onReSelect, primary = state.identityControls)
    }) {
        WorkflowHeader("Your results", onBack)
        if (state.identityControls) {
            InfoPanel(stringResource(R.string.result_unchanged_title), stringResource(R.string.result_unchanged_detail))
            val heightLimit = (LocalConfiguration.current.screenHeightDp * .40f).coerceIn(160f, 480f).dp
            Surface(Modifier.fillMaxWidth(), shape = PhotoShape) {
                AsyncImage(
                    model = before,
                    contentDescription = stringResource(R.string.result_before),
                    modifier = Modifier.fillMaxWidth().padding(12.dp).heightIn(max = heightLimit),
                    contentScale = ContentScale.Fit
                )
            }
        } else {
            val info = photoInfo(after)
            info?.let { PhotoComparison(before, after, it.width.toFloat() / it.height) }
            InfoPanel("Correction complete", "Your photo is ready to save.")
        }
        if (message.isNotEmpty()) Text(message, style = MaterialTheme.typography.bodySmall)
    }
}

@Composable
private fun PhotoComparison(before: Uri, after: Uri, aspectRatio: Float) {
    var split by rememberSaveable(before, after) { mutableFloatStateOf(.5f) }
    val previewLimit = (LocalConfiguration.current.screenHeightDp * .48f).coerceIn(180f, 560f).dp
    Surface(Modifier.fillMaxWidth(), shape = PhotoShape) {
        Column(Modifier.padding(12.dp), horizontalAlignment = Alignment.CenterHorizontally) {
            Row(Modifier.fillMaxWidth().padding(bottom = 10.dp), horizontalArrangement = Arrangement.SpaceBetween) {
                Text("Before", style = MaterialTheme.typography.labelLarge)
                Text("After", style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.primary)
            }
            BoxWithConstraints(Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) {
                val photoWidth = maxWidth.coerceAtMost(previewLimit * aspectRatio)
                Box(Modifier.width(photoWidth).aspectRatio(aspectRatio)
                    .pointerInput(before, after) {
                        detectHorizontalDragGestures(
                            onDragStart = { split = (it.x / size.width).coerceIn(0f, 1f) }
                        ) { change, _ ->
                            split = (change.position.x / size.width).coerceIn(0f, 1f)
                        }
                    }) {
                    AsyncImage(after, "Corrected photo", Modifier.matchParentSize(), contentScale = ContentScale.Fit)
                    AsyncImage(before, "Original photo", Modifier.matchParentSize().drawWithContent {
                        clipRect(right = size.width * split) { this@drawWithContent.drawContent() }
                    }, contentScale = ContentScale.Fit)
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
