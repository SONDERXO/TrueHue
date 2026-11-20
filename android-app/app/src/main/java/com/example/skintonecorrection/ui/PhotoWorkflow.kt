package com.example.skintonecorrection.ui

import android.graphics.BitmapFactory
import android.net.Uri
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import java.io.IOException
import java.util.Locale
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlin.math.cos
import kotlin.math.sin

internal val PhotoShape = RoundedCornerShape(20.dp)

@Composable
internal fun WorkflowPage(
    actions: @Composable ColumnScope.() -> Unit,
    content: @Composable ColumnScope.() -> Unit
) {
    val background = MaterialTheme.colorScheme.background
    Scaffold(
        containerColor = background,
        bottomBar = {
            Surface(color = background) {
                Box(Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) {
                    Column(
                        Modifier.widthIn(max = 480.dp).fillMaxWidth().navigationBarsPadding()
                            .padding(horizontal = 20.dp, vertical = 12.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp),
                        content = actions
                    )
                }
            }
        }
    ) { insets ->
        Box(Modifier.fillMaxSize().padding(insets), contentAlignment = Alignment.TopCenter) {
            Column(
                Modifier.widthIn(max = 480.dp).fillMaxWidth().verticalScroll(rememberScrollState())
                    .padding(horizontal = 20.dp, vertical = 14.dp),
                verticalArrangement = Arrangement.spacedBy(14.dp),
                content = content
            )
        }
    }
}

@Composable
internal fun WorkflowHeader(title: String, onBack: () -> Unit) {
    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
        IconButton(onClick = onBack, modifier = Modifier.semantics { contentDescription = "Back" }) {
            val ink = MaterialTheme.colorScheme.onSurface
            Canvas(Modifier.size(16.dp)) {
                val tip = Offset(size.width * .35f, center.y)
                drawLine(ink, Offset(size.width * .65f, size.height * .20f), tip, 2.dp.toPx(), StrokeCap.Round)
                drawLine(ink, tip, Offset(size.width * .65f, size.height * .80f), 2.dp.toPx(), StrokeCap.Round)
            }
        }
        Text(title, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
    }
}

@Composable
internal fun BrandMark() {
    Surface(color = MaterialTheme.colorScheme.primary, shape = RoundedCornerShape(14.dp)) {
        val ink = MaterialTheme.colorScheme.onPrimary
        Canvas(Modifier.size(48.dp)) {
            drawCircle(ink, radius = 4.dp.toPx(), style = Stroke(1.4.dp.toPx()))
            for (ray in 0 until 8) {
                val angle = ray * Math.PI / 4.0
                val direction = Offset(cos(angle).toFloat(), sin(angle).toFloat())
                drawLine(ink, center + direction * 8.dp.toPx(), center + direction * 11.dp.toPx(),
                    strokeWidth = 1.5.dp.toPx(), cap = StrokeCap.Round)
            }
        }
    }
}

@Composable
internal fun WorkflowAction(label: String, onClick: () -> Unit, enabled: Boolean = true, primary: Boolean = true) {
    val modifier = Modifier.fillMaxWidth().heightIn(min = 50.dp)
    val shape = RoundedCornerShape(16.dp)
    if (primary) {
        Button(onClick = onClick, enabled = enabled, modifier = modifier, shape = shape) { Text(label) }
    } else {
        OutlinedButton(onClick = onClick, enabled = enabled, modifier = modifier, shape = shape) { Text(label) }
    }
}

@Composable
internal fun InfoPanel(title: String, detail: String, caution: Boolean = false) {
    val scheme = MaterialTheme.colorScheme
    val container = if (caution) scheme.tertiaryContainer else scheme.primaryContainer
    val ink = if (caution) scheme.onTertiaryContainer else scheme.onPrimaryContainer
    Surface(Modifier.fillMaxWidth(), color = container, contentColor = ink, shape = RoundedCornerShape(16.dp)) {
        Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(3.dp)) {
            Text(title, style = MaterialTheme.typography.titleSmall)
            Text(detail, style = MaterialTheme.typography.bodySmall)
        }
    }
}

internal data class PhotoInfo(val width: Int, val height: Int, val format: String?) {
    val resolution get() = "$width × $height"
}

@Composable
internal fun photoInfo(uri: Uri?): PhotoInfo? {
    val resolver = LocalContext.current.contentResolver
    return produceState<PhotoInfo?>(null, uri, resolver) {
        value = null
        if (uri == null) return@produceState
        value = withContext(Dispatchers.IO) {
            try {
                val options = BitmapFactory.Options().apply { inJustDecodeBounds = true }
                resolver.openInputStream(uri)?.use { BitmapFactory.decodeStream(it, null, options) }
                if (options.outWidth > 0 && options.outHeight > 0) {
                    PhotoInfo(options.outWidth, options.outHeight,
                        options.outMimeType?.substringAfterLast('/')?.uppercase(Locale.ROOT))
                } else null
            } catch (_: IOException) {
                null
            } catch (_: SecurityException) {
                null
            }
        }
    }.value
}
