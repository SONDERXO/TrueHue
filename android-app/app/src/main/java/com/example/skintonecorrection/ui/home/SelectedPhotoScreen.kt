package com.example.skintonecorrection.ui.home

import android.net.Uri
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
import com.example.skintonecorrection.ui.InfoPanel
import com.example.skintonecorrection.ui.PhotoShape
import com.example.skintonecorrection.ui.WorkflowAction
import com.example.skintonecorrection.ui.WorkflowHeader
import com.example.skintonecorrection.ui.WorkflowPage
import com.example.skintonecorrection.ui.photoInfo

@Composable
fun SelectedPhotoScreen(photo: Uri, onBack: () -> Unit, onPickPhoto: () -> Unit, onApply: () -> Unit) {
    val info = photoInfo(photo)
    val previewHeight = (LocalConfiguration.current.screenHeightDp * .33f).coerceIn(190f, 310f).dp
    WorkflowPage(actions = {
        WorkflowAction("Apply correction", onApply)
        WorkflowAction("Choose a different photo", onPickPhoto, primary = false)
    }) {
        WorkflowHeader("Selected photo", onBack)
        AsyncImage(model = photo, contentDescription = "Selected photo",
            modifier = Modifier.fillMaxWidth().height(previewHeight).clip(PhotoShape)
                .background(MaterialTheme.colorScheme.surfaceVariant),
            contentScale = ContentScale.Fit)
        if (info != null) {
            Surface(Modifier.fillMaxWidth(), shape = PhotoShape) {
                Row(Modifier.fillMaxWidth().padding(16.dp), horizontalArrangement = Arrangement.SpaceEvenly) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text(info.resolution, style = MaterialTheme.typography.titleSmall)
                        Text("File resolution", style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                    info.format?.let { format ->
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text(format, style = MaterialTheme.typography.titleSmall)
                            Text("Format", style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant)
                        }
                    }
                }
            }
        }
        InfoPanel("For best results", "Use a well-lit, front-facing portrait.", caution = true)
    }
}
